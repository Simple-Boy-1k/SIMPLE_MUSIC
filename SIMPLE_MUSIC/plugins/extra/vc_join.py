import asyncio
import html
import config
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_known_participants: dict[int, set[int]] = {}
_tracked_assistants: list[Client] = []
_main_bot_ref: Client | None = None
_poll_task_started = False


def _format_vc_join_text(
    user_name: str,
    user_id: int,
    username: str | None,
    group_title: str,
) -> str:
    safe_name = html.escape(user_name)
    safe_group = html.escape(group_title)
    user_mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'
    username_line = f"@{html.escape(username)}" if username else "None"

    return (
        "🎙 <b>USER JOINED VOICE CHAT</b>\n"
        f"👤 <b>USER:</b> {user_mention}\n"
        f"⚡ <b>USERNAME:</b> {username_line}\n"
        f"👥 <b>GROUP:</b> {safe_group}\n"
        "<blockquote><b>✨ TAP BELOW TO JOIN ✨</b></blockquote>"
    )


def _format_vc_join_buttons(
    chat_id: int,
    user_id: int,
    bot_username: str | None = None,
) -> InlineKeyboardMarkup:
    clean_id = str(chat_id).replace("-100", "")
    vc_link = f"https://t.me/c/{clean_id}/1?videochat"
    add_bot_url = (
        f"https://t.me/{bot_username}?startgroup=true"
        if bot_username
        else f"tg://user?id={user_id}"
    )
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎧 Join VC", url=vc_link),
                InlineKeyboardButton("➕ Add Me", url=add_bot_url),
            ]
        ]
    )


async def _is_bot_admin_in_gc(main_bot: Client, chat_id: int) -> bool:
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        return False

    try:
        me = main_bot.me or await main_bot.get_me()
        member = await main_bot.get_chat_member(chat_id, me.id)
        status_str = str(getattr(member, "status", "")).upper()
        return "ADMINISTRATOR" in status_str or "OWNER" in status_str
    except Exception as e:
        print(f"[VC DEBUG] Admin check failed in {chat_id}: {e}")
        return False


async def _send_join_alert(
    assistant_client: Client,
    main_bot: Client,
    chat_id: int,
    group_title: str,
    user_id: int,
):
    if not await _is_bot_admin_in_gc(main_bot, chat_id):
        print(f"[VC DEBUG] Skipped {chat_id}: bot not admin or logger group")
        return

    user_name = f"User {user_id}"
    username = None
    try:
        tg_user = await assistant_client.get_users(user_id)
        first = getattr(tg_user, "first_name", "") or ""
        last = f" {tg_user.last_name}" if getattr(tg_user, "last_name", None) else ""
        full = f"{first}{last}".strip()
        if full:
            user_name = full
        username = getattr(tg_user, "username", None)
    except Exception:
        pass

    me = main_bot.me or await main_bot.get_me()
    bot_username = getattr(me, "username", None)

    text = _format_vc_join_text(
        user_name=user_name,
        user_id=user_id,
        username=username,
        group_title=group_title,
    )
    reply_markup = _format_vc_join_buttons(
        chat_id=chat_id,
        user_id=user_id,
        bot_username=bot_username,
    )

    try:
        await main_bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        print(f"[VC DEBUG] Alert sent to {chat_id} for {user_id}")
    except Exception as e:
        print(f"[VC DEBUG] Send failed in {chat_id}: {e}")


async def _check_chat_vc_participants(assistant_client: Client, main_bot: Client, chat):
    chat_id = int(chat.id)
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and chat_id == int(logger_id):
        return

    try:
        peer = await assistant_client.resolve_peer(chat_id)
        if not isinstance(peer, types.InputPeerChannel):
            return

        full_chat = await assistant_client.invoke(
            functions.channels.GetFullChannel(channel=peer)
        )
        call = getattr(full_chat.full_chat, "call", None)
        if not call:
            _known_participants.pop(chat_id, None)
            return

        input_call = types.InputGroupCall(
            id=call.id,
            access_hash=call.access_hash,
        )
        res = await assistant_client.invoke(
            functions.phone.GetGroupParticipants(
                call=input_call,
                ids=[],
                sources=[],
                offset="",
                limit=100,
            )
        )

        current_ids: set[int] = set()
        for p in getattr(res, "participants", []) or []:
            p_peer = getattr(p, "peer", None)
            uid = getattr(p_peer, "user_id", None)
            if uid:
                current_ids.add(int(uid))

        prev_ids = _known_participants.get(chat_id)
        if prev_ids is None:
            # Pehli scan mein existing members baseline set karo
            _known_participants[chat_id] = current_ids
            return

        joined_ids = current_ids - prev_ids
        _known_participants[chat_id] = current_ids

        group_title = getattr(chat, "title", None) or "Group"
        for uid in joined_ids:
            await _send_join_alert(
                assistant_client=assistant_client,
                main_bot=main_bot,
                chat_id=chat_id,
                group_title=group_title,
                user_id=uid,
            )
    except Exception as e:
        print(f"[VC DEBUG] Poll error in {chat_id}: {e}")


async def _poll_vc_joins_loop():
    global _poll_task_started
    try:
        while True:
            await asyncio.sleep(5)
            main_bot = _main_bot_ref
            if not main_bot:
                continue

            for client in list(_tracked_assistants):
                try:
                    async for dialog in client.get_dialogs():
                        chat = getattr(dialog, "chat", None)
                        if not chat:
                            continue
                        chat_type = str(getattr(chat, "type", "")).lower()
                        if "supergroup" in chat_type or "channel" in chat_type:
                            await _check_chat_vc_participants(client, main_bot, chat)
                            await asyncio.sleep(0.15)
                except Exception as e:
                    print(f"[VC DEBUG] Dialog loop error: {e}")
    finally:
        _poll_task_started = False


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    global _main_bot_ref, _poll_task_started
    _main_bot_ref = main_bot

    if assistant_client not in _tracked_assistants:
        _tracked_assistants.append(assistant_client)

    try:
        loop = asyncio.get_running_loop()
        if not _poll_task_started:
            _poll_task_started = True
            loop.create_task(_poll_vc_joins_loop())
            print("[VC DEBUG] Started VC join poller")
    except RuntimeError as e:
        print(f"[VC DEBUG] Failed to start poller: {e}")
