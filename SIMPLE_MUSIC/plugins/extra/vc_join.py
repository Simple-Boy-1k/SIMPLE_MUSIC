import asyncio
import html
import time
import config
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_call_to_chat_id: dict[int, int] = {}
_chat_to_call_id: dict[int, int] = {}
_call_participants: dict[int, set[int]] = {}
_recent_alerts: dict[tuple[int, int], float] = {}
_last_gc_chat_id: int | None = None
_tracked_assistants: list[Client] = []
_refresh_loop_running = False


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


def _normalize_channel_chat_id(raw_val) -> int | None:
    if raw_val is None:
        return None
    s = str(raw_val)
    if s.startswith("-100"):
        return int(s) if s[4:].isdigit() else None
    if s.startswith("-"):
        return int(s) if s[1:].isdigit() else None
    if s.isdigit():
        return int(f"-100{s}")
    return None


def _extract_call_id(update) -> int | None:
    call_obj = getattr(update, "call", None)
    call_id = getattr(call_obj, "id", None)
    return int(call_id) if call_id else None


def _extract_chat_id(update, chats: dict) -> int | None:
    if getattr(update, "chat_id", None):
        cid = _normalize_channel_chat_id(update.chat_id)
        if cid:
            return cid

    peer = getattr(update, "peer", None)
    if peer:
        if getattr(peer, "channel_id", None):
            cid = _normalize_channel_chat_id(peer.channel_id)
            if cid:
                return cid
        if getattr(peer, "chat_id", None):
            return -abs(int(peer.chat_id))

    if chats:
        for chat_key, chat_obj in chats.items():
            raw_id = getattr(chat_obj, "id", None) or chat_key
            cid = _normalize_channel_chat_id(raw_id)
            if cid:
                return cid

    call_id = _extract_call_id(update)
    if call_id and call_id in _call_to_chat_id:
        return _call_to_chat_id[call_id]

    return _last_gc_chat_id


async def _subscribe_chat_call(client: Client, chat_id: int):
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        return

    try:
        peer = await client.resolve_peer(chat_id)
        if not isinstance(peer, types.InputPeerChannel):
            return

        full_chat = await client.invoke(functions.channels.GetFullChannel(channel=peer))
        call = getattr(full_chat.full_chat, "call", None)
        if not call:
            return

        call_id = int(call.id)
        _call_to_chat_id[call_id] = int(chat_id)
        _chat_to_call_id[int(chat_id)] = call_id

        input_call = types.InputGroupCall(
            id=call.id,
            access_hash=call.access_hash,
        )
        res = await client.invoke(
            functions.phone.GetGroupCall(
                call=input_call,
                limit=100,
            )
        )
        existing_ids: set[int] = set()
        for p in getattr(res, "participants", []) or []:
            p_peer = getattr(p, "peer", None)
            uid = getattr(p_peer, "user_id", None)
            if uid:
                existing_ids.add(int(uid))
        _call_participants.setdefault(call_id, set()).update(existing_ids)
    except Exception:
        pass


async def _periodic_call_subscriber():
    global _refresh_loop_running
    try:
        while True:
            await asyncio.sleep(30)
            for client in list(_tracked_assistants):
                try:
                    async for dialog in client.get_dialogs():
                        chat = getattr(dialog, "chat", None)
                        if not chat:
                            continue
                        chat_type = str(getattr(chat, "type", "")).lower()
                        if "supergroup" in chat_type or "channel" in chat_type:
                            await _subscribe_chat_call(client, chat.id)
                            await asyncio.sleep(0.2)
                except Exception:
                    pass
    finally:
        _refresh_loop_running = False


async def _is_bot_admin_in_gc(main_bot: Client, chat_id: int) -> bool:
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        return False

    try:
        bot_id = main_bot.me.id
        member = await main_bot.get_chat_member(chat_id, bot_id)
        status = getattr(member, "status", None)
        status_str = str(status).upper()
        return (
            status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
            or "ADMINISTRATOR" in status_str
            or "OWNER" in status_str
        )
    except Exception:
        return False


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    global _refresh_loop_running

    if assistant_client not in _tracked_assistants:
        _tracked_assistants.append(assistant_client)

    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        global _last_gc_chat_id

        if isinstance(update, types.UpdateGroupCall):
            cid = _extract_chat_id(update, chats)
            call_id = _extract_call_id(update)
            logger_id = getattr(config, "LOGGER_ID", None)
            if cid and not (logger_id and int(cid) == int(logger_id)):
                _last_gc_chat_id = cid
                if call_id:
                    _call_to_chat_id[call_id] = cid
                    _chat_to_call_id[cid] = call_id
                    _call_participants.setdefault(call_id, set())
                await _subscribe_chat_call(client, cid)
            return

        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        call_id = _extract_call_id(update)
        chat_id = _extract_chat_id(update, chats)
        if not chat_id:
            return

        if call_id:
            _call_to_chat_id[call_id] = chat_id
            _chat_to_call_id[chat_id] = call_id

        if not await _is_bot_admin_in_gc(main_bot, chat_id):
            return

        tracked_key = call_id if call_id else chat_id
        active_set = _call_participants.setdefault(tracked_key, set())
        bot_username = getattr(getattr(main_bot, "me", None), "username", None)
        now = time.monotonic()

        for participant in getattr(update, "participants", []):
            left = bool(getattr(participant, "left", False))
            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            if not user_id:
                continue

            user_id = int(user_id)
            if left:
                active_set.discard(user_id)
                continue

            # Duplicate spam rokne ke liye 2 second cooldown
            alert_key = (int(chat_id), user_id)
            last_sent = _recent_alerts.get(alert_key, 0.0)
            if now - last_sent < 2.0:
                continue
            _recent_alerts[alert_key] = now
            active_set.add(user_id)

            user_name = None
            username = None

            if user_id in users:
                u = users[user_id]
                first = getattr(u, "first_name", "") or ""
                last = f" {getattr(u, 'last_name', '')}" if getattr(u, "last_name", None) else ""
                user_name = f"{first}{last}".strip()
                username = getattr(u, "username", None)

            if not user_name or not username:
                try:
                    tg_user = await client.get_users(user_id)
                    if not user_name:
                        first = tg_user.first_name or ""
                        last = f" {tg_user.last_name}" if tg_user.last_name else ""
                        user_name = f"{first}{last}".strip()
                    if not username:
                        username = tg_user.username
                except Exception:
                    pass

            user_name = user_name or f"User {user_id}"

            group_title = "Group"
            if chats:
                for _, chat_obj in chats.items():
                    title = getattr(chat_obj, "title", None)
                    if title:
                        group_title = title
                        break

            if group_title == "Group":
                try:
                    chat_obj = await client.get_chat(chat_id)
                    group_title = chat_obj.title or group_title
                except Exception:
                    pass

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
            except Exception as exc:
                print(f"[VC Notifier] Failed sending in {chat_id}: {exc}")

    try:
        loop = asyncio.get_running_loop()
        if not _refresh_loop_running:
            _refresh_loop_running = True
            loop.create_task(_periodic_call_subscriber())
    except RuntimeError:
        pass
