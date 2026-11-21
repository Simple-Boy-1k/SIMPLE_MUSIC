import html
import config
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_call_to_chat_id: dict[int, int] = {}
_last_gc_chat_id: int | None = None


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


def _extract_chat_id(update, chats: dict) -> int | None:
    global _last_gc_chat_id

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

    call_obj = getattr(update, "call", None)
    call_id = getattr(call_obj, "id", None)
    if call_id and int(call_id) in _call_to_chat_id:
        return _call_to_chat_id[int(call_id)]

    return _last_gc_chat_id


async def _is_bot_admin_in_gc(main_bot: Client, chat_id: int) -> bool:
    """Logger group ko chhodkar sirf un GCs ko allow karta hai jahan main_bot admin/owner hai."""
    logger_id = getattr(config, "LOGGER_ID", None)
    if logger_id and int(chat_id) == int(logger_id):
        print(f"[VC DEBUG] Skipped logger group {chat_id}")
        return False

    try:
        bot_id = main_bot.me.id
        member = await main_bot.get_chat_member(chat_id, bot_id)
        status = getattr(member, "status", None)
        status_str = str(status).upper()
        is_admin = (
            status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
            or "ADMINISTRATOR" in status_str
            or "OWNER" in status_str
        )
        print(f"[VC DEBUG] chat_id={chat_id}, bot_status={status}, is_admin={is_admin}")
        return is_admin
    except Exception as e:
        print(f"[VC DEBUG] get_chat_member failed for {chat_id}: {e}")
        return False


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        global _last_gc_chat_id

        if isinstance(update, types.UpdateGroupCall):
            cid = _extract_chat_id(update, chats)
            call_obj = getattr(update, "call", None)
            call_id = getattr(call_obj, "id", None)
            logger_id = getattr(config, "LOGGER_ID", None)
            if cid and not (logger_id and int(cid) == int(logger_id)):
                _last_gc_chat_id = cid
                if call_id:
                    _call_to_chat_id[int(call_id)] = cid
                print(f"[VC DEBUG] Tracked GC call_id={call_id} -> chat_id={cid}")
            return

        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        chat_id = _extract_chat_id(update, chats)
        print(f"[VC DEBUG] Participants update -> chat_id={chat_id}, chats_keys={list(chats.keys()) if chats else []}")
        if not chat_id:
            return

        if not await _is_bot_admin_in_gc(main_bot, chat_id):
            return

        bot_username = getattr(getattr(main_bot, "me", None), "username", None)

        for participant in getattr(update, "participants", []):
            if getattr(participant, "left", False):
                continue

            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            if not user_id:
                continue

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
                print(f"[VC DEBUG] Sent VC alert to {chat_id} for user_id={user_id}")
            except Exception as exc:
                print(f"[VC DEBUG] Failed sending in {chat_id}: {exc}")
