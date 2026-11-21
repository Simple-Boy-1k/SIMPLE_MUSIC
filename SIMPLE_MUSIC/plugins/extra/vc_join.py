import asyncio
import html
import config
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_known_participants: dict[int, set[int]] = {}
_tracked_assistants: list[Client] = []
_app: Client | None = None
_loop_started = False
AUTO_DELETE_SECONDS = 20


def _format_vc_event_text(
    event_type: str,
    user_name: str,
    user_id: int,
    username: str | None,
    group_title: str,
) -> str:
    safe_name = html.escape(user_name)
    safe_group = html.escape(group_title)
    user_mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'
    username_line = f"@{html.escape(username)}" if username else "None"

    if event_type == "join":
        header = "🎙 <b>USER JOINED VOICE CHAT</b>"
        quote = "<blockquote><b>✨ TAP BELOW TO JOIN ✨</b></blockquote>"
    else:
        header = "🚪 <b>USER LEFT VOICE CHAT</b>"
        quote = "<blockquote><b>🌙 LEFT THE VOICE CHAT 🌙</b></blockquote>"

    return (
        f"{header}\n"
        f"👤 <b>USER:</b> {user_mention}\n"
        f"⚡ <b>USERNAME:</b> {username_line}\n"
        f"👥 <b>GROUP:</b> {safe_group}\n"
        f"{quote}"
    )


def _format_vc_buttons(
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


async def _delete_after_delay(message, delay: int = AUTO_DELETE_SECONDS):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def _is_bot_admin(bot: Client, chat_id: int) -> bool:
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        return False

    try:
        me = bot.me or await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
        status_str = str(getattr(member, "status", "")).upper()
        return "ADMINISTRATOR" in status_str or "OWNER" in status_str
    except Exception:
        return False


async def _send_vc_alert(
    assistant: Client,
    bot: Client,
    chat_id: int,
    group_title: str,
    user_id: int,
    event_type: str,
):
    if not await _is_bot_admin(bot, chat_id):
        return

    user_name = f"User {user_id}"
    username = None
    try:
        user = await assistant.get_users(user_id)
        first = getattr(user, "first_name", "") or ""
        last = f" {user.last_name}" if getattr(user, "last_name", None) else ""
        full_name = f"{first}{last}".strip()
        if full_name:
            user_name = full_name
        username = getattr(user, "username", None)
    except Exception:
        pass

    me = bot.me or await bot.get_me()
    bot_username = getattr(me, "username", None)

    text = _format_vc_event_text(
        event_type=event_type,
        user_name=user_name,
        user_id=user_id,
        username=username,
        group_title=group_title,
    )
    reply_markup = _format_vc_buttons(
        chat_id=chat_id,
        user_id=user_id,
        bot_username=bot_username,
    )

    try:
        sent_msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        asyncio.create_task(_delete_after_delay(sent_msg, AUTO_DELETE_SECONDS))
    except Exception as e:
        print(f"[VC Join] Send error in {chat_id}: {e}")


async def _scan_chat_vc(assistant: Client, bot: Client, chat):
    chat_id = int(chat.id)
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and chat_id == int(logger_id):
        return

    try:
        peer = await assistant.resolve_peer(chat_id)
        if not isinstance(peer, types.InputPeerChannel):
            return

        full_chat = await assistant.invoke(
            functions.channels.GetFullChannel(channel=peer)
        )
        call = getattr(full_chat.full_chat, "call", None)
        if not call:
            prev_ids = _known_participants.pop(chat_id, None)
            if prev_ids:
                group_title = getattr(chat, "title", None) or "Group"
                for uid in prev_ids:
                    await _send_vc_alert(
                        assistant=assistant,
                        bot=bot,
                        chat_id=chat_id,
                        group_title=group_title,
                        user_id=uid,
                        event_type="left",
                    )
            return

        input_call = types.InputGroupCall(
            id=call.id,
            access_hash=call.access_hash,
        )
        res = await assistant.invoke(
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
            _known_participants[chat_id] = current_ids
            return

        joined_ids = current_ids - prev_ids
        left_ids = prev_ids - current_ids
        _known_participants[chat_id] = current_ids

        group_title = getattr(chat, "title", None) or "Group"
        for uid in joined_ids:
            await _send_vc_alert(
                assistant=assistant,
                bot=bot,
                chat_id=chat_id,
                group_title=group_title,
                user_id=uid,
                event_type="join",
            )
        for uid in left_ids:
            await _send_vc_alert(
                assistant=assistant,
                bot=bot,
                chat_id=chat_id,
                group_title=group_title,
                user_id=uid,
                event_type="left",
            )
    except Exception:
        pass


async def _vc_watcher_loop():
    global _loop_started
    try:
        while True:
            await asyncio.sleep(5)
            bot = _app
            if not bot:
                continue

            for assistant in list(_tracked_assistants):
                try:
                    async for dialog in assistant.get_dialogs():
                        chat = getattr(dialog, "chat", None)
                        if not chat:
                            continue
                        chat_type = str(getattr(chat, "type", "")).lower()
                        if "supergroup" in chat_type or "channel" in chat_type:
                            await _scan_chat_vc(assistant, bot, chat)
                            await asyncio.sleep(0.15)
                except Exception:
                    pass
    finally:
        _loop_started = False


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    global _app, _loop_started
    _app = main_bot

    if assistant_client not in _tracked_assistants:
        _tracked_assistants.append(assistant_client)

    try:
        loop = asyncio.get_running_loop()
        if not _loop_started:
            _loop_started = True
            loop.create_task(_vc_watcher_loop())
    except RuntimeError:
        pass
