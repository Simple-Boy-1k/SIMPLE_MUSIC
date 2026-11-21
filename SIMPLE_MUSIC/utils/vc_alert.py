import asyncio
import html
import time
import config
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

AUTO_DELETE_SECONDS = 20

_known_participants: dict[int, set[int]] = {}
_known_chats: dict[int, str] = {}
_call_to_chat_id: dict[int, int] = {}
_recent_alerts: dict[tuple[str, int, int], float] = {}
_tracked_assistants: list[Client] = []
_app: Client | None = None
_poller_started = False


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
        header = "🎙 <b>ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</b>"
        quote = "<b>ᴛᴀʙ ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ</b>"
    else:
        header = "🚪 <b>ᴜꜱᴇʀ ʟᴇꜰᴛ ᴠᴄ ᴄʜᴀᴛ</b>"
        quote = "<b>ʟᴇꜰᴛ ᴛʜᴇ ᴠᴄ  🌙</b>"

    return (
        "<blockquote>"
        f"{header}\n"
        f"👤 <b>ᴜꜱᴇʀ:</b> {user_mention}\n"
        f"⚡ <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> {username_line}\n"
        f"👥 <b>ɢʀᴏᴜᴩ:</b> {safe_group}\n"
        f"{quote}"
        "</blockquote>"
    )


def _make_danger_button(text: str, url: str) -> InlineKeyboardButton:
    try:
        return InlineKeyboardButton(text=text, url=url, style="danger")
    except TypeError:
        return InlineKeyboardButton(text=text, url=url)


def _format_vc_buttons(
    chat_id: int,
    user_id: int,
    bot_username: str | None = None,
) -> InlineKeyboardMarkup:
    clean_id = str(chat_id).replace("-100", "").lstrip("-")
    vc_link = f"https://t.me/c/{clean_id}/1?videochat"
    add_bot_url = (
        f"https://t.me/{bot_username}?startgroup=true"
        if bot_username
        else f"tg://user?id={user_id}"
    )
    return InlineKeyboardMarkup(
        [
            [
                _make_danger_button("🎧 Join VC", vc_link),
                _make_danger_button("➕ Add Me", add_bot_url),
            ]
        ]
    )


def _normalize_channel_id(raw_val) -> int | None:
    if raw_val is None:
        return None
    s = str(raw_val).strip()
    if s.startswith("-100") and s[4:].isdigit():
        return int(s)
    if s.startswith("-") and s[1:].isdigit():
        return int(s)
    if s.isdigit():
        return int(f"-100{s}")
    return None


def _extract_call_id(update) -> int | None:
    call_obj = getattr(update, "call", None)
    call_id = getattr(call_obj, "id", None)
    return int(call_id) if call_id else None


def _extract_chat_id(update, chats: dict) -> int | None:
    if getattr(update, "chat_id", None):
        cid = _normalize_channel_id(update.chat_id)
        if cid:
            return cid

    peer = getattr(update, "peer", None)
    if peer:
        if getattr(peer, "channel_id", None):
            cid = _normalize_channel_id(peer.channel_id)
            if cid:
                return cid
        if getattr(peer, "chat_id", None):
            return -abs(int(peer.chat_id))

    if chats:
        for chat_key, chat_obj in chats.items():
            raw_id = getattr(chat_obj, "id", None) or chat_key
            cid = _normalize_channel_id(raw_id)
            if cid:
                return cid

    call_id = _extract_call_id(update)
    if call_id and call_id in _call_to_chat_id:
        return _call_to_chat_id[call_id]

    return None


async def _delete_after_delay(message, delay: int = AUTO_DELETE_SECONDS):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def _is_bot_admin_in_gc(bot: Client, chat_id: int) -> bool:
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        return False

    try:
        me = bot.me or await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
        status = getattr(member, "status", None)
        status_str = str(status).upper()
        return (
            status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
            or "ADMINISTRATOR" in status_str
            or "OWNER" in status_str
        )
    except Exception:
        return False


async def _dispatch_alert(
    assistant: Client,
    bot: Client,
    chat_id: int,
    group_title: str,
    user_id: int,
    event_type: str,
    users_cache: dict | None = None,
):
    chat_id = int(chat_id)
    user_id = int(user_id)

    if not await _is_bot_admin_in_gc(bot, chat_id):
        return

    now = time.monotonic()
    key = (event_type, chat_id, user_id)
    if now - _recent_alerts.get(key, 0.0) < 3.0:
        return
    _recent_alerts[key] = now

    user_name = None
    username = None

    if users_cache and user_id in users_cache:
        u = users_cache[user_id]
        first = getattr(u, "first_name", "") or ""
        last = f" {getattr(u, 'last_name', '')}" if getattr(u, "last_name", None) else ""
        user_name = f"{first}{last}".strip() or None
        username = getattr(u, "username", None)

    if not user_name or username is None:
        try:
            tg_user = await assistant.get_users(user_id)
            if not user_name:
                first = getattr(tg_user, "first_name", "") or ""
                last = f" {getattr(tg_user, 'last_name', '')}" if getattr(tg_user, "last_name", None) else ""
                user_name = f"{first}{last}".strip() or None
            if username is None:
                username = getattr(tg_user, "username", None)
        except Exception:
            pass

    user_name = user_name or f"User {user_id}"

    if not group_title or group_title == "Group":
        group_title = _known_chats.get(chat_id) or "Group"
    if group_title == "Group":
        try:
            chat_obj = await bot.get_chat(chat_id)
            group_title = getattr(chat_obj, "title", None) or "Group"
        except Exception:
            pass

    _known_chats[chat_id] = group_title

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
    except Exception as exc:
        print(f"[VC Alert] Send error in {chat_id}: {exc}")


async def _fetch_all_participants(assistant: Client, input_call: types.InputGroupCall) -> set[int]:
    ids: set[int] = set()
    offset = ""
    while True:
        res = await assistant.invoke(
            functions.phone.GetGroupParticipants(
                call=input_call,
                ids=[],
                sources=[],
                offset=offset,
                limit=100,
            )
        )
        batch = getattr(res, "participants", []) or []
        if not batch:
            break

        for p in batch:
            p_peer = getattr(p, "peer", None)
            uid = getattr(p_peer, "user_id", None)
            if uid:
                ids.add(int(uid))

        next_offset = getattr(res, "next_offset", None)
        if not next_offset or next_offset == offset or len(batch) < 100:
            break
        offset = next_offset
    return ids


async def _sync_chat_vc(assistant: Client, bot: Client, chat_id: int, group_title: str | None = None):
    chat_id = int(chat_id)
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and chat_id == int(logger_id):
        return

    title = group_title or _known_chats.get(chat_id) or "Group"
    if group_title:
        _known_chats[chat_id] = group_title

    try:
        try:
            peer = await assistant.resolve_peer(chat_id)
        except Exception:
            chat_obj = await assistant.get_chat(chat_id)
            title = getattr(chat_obj, "title", None) or title
            _known_chats[chat_id] = title
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
                for uid in prev_ids:
                    await _dispatch_alert(
                        assistant=assistant,
                        bot=bot,
                        chat_id=chat_id,
                        group_title=title,
                        user_id=uid,
                        event_type="left",
                    )
            return

        call_id = int(call.id)
        _call_to_chat_id[call_id] = chat_id

        input_call = types.InputGroupCall(
            id=call.id,
            access_hash=call.access_hash,
        )
        current_ids = await _fetch_all_participants(assistant, input_call)

        prev_ids = _known_participants.get(chat_id)
        if prev_ids is None:
            _known_participants[chat_id] = current_ids
            return

        joined_ids = current_ids - prev_ids
        left_ids = prev_ids - current_ids
        _known_participants[chat_id] = current_ids

        for uid in joined_ids:
            await _dispatch_alert(
                assistant=assistant,
                bot=bot,
                chat_id=chat_id,
                group_title=title,
                user_id=uid,
                event_type="join",
            )

        for uid in left_ids:
            await _dispatch_alert(
                assistant=assistant,
                bot=bot,
                chat_id=chat_id,
                group_title=title,
                user_id=uid,
                event_type="left",
            )
    except Exception:
        pass


async def _vc_poller_loop():
    global _poller_started
    try:
        while True:
            await asyncio.sleep(2.5)
            bot = _app
            if not bot:
                continue

            seen_chats: set[int] = set()
            for assistant in list(_tracked_assistants):
                try:
                    async for dialog in assistant.get_dialogs():
                        chat = getattr(dialog, "chat", None)
                        if not chat:
                            continue
                        cid = int(chat.id)
                        if cid in seen_chats:
                            continue
                        chat_type = str(getattr(chat, "type", "")).lower()
                        if "supergroup" in chat_type or "channel" in chat_type:
                            seen_chats.add(cid)
                            title = getattr(chat, "title", None) or "Group"
                            await _sync_chat_vc(assistant, bot, cid, title)
                            await asyncio.sleep(0.08)
                except Exception:
                    pass
    finally:
        _poller_started = False


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    global _app, _poller_started
    _app = main_bot

    if assistant_client not in _tracked_assistants:
        _tracked_assistants.append(assistant_client)

    @assistant_client.on_raw_update()
    async def _on_raw_vc_update(client: Client, update, users: dict, chats: dict):
        bot = _app
        if not bot:
            return

        if chats:
            for _, chat_obj in chats.items():
                cid = _normalize_channel_id(getattr(chat_obj, "id", None))
                title = getattr(chat_obj, "title", None)
                if cid and title:
                    _known_chats[cid] = title

        if isinstance(update, types.UpdateGroupCall):
            cid = _extract_chat_id(update, chats)
            call_id = _extract_call_id(update)
            if cid and call_id:
                _call_to_chat_id[call_id] = cid
            if cid:
                await _sync_chat_vc(client, bot, cid
