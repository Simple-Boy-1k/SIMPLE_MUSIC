from pyrogram import Client
from pyrogram.raw import types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_last_vc_chat_id: int | None = None


def _format_vc_join_text(user_name: str, group_title: str) -> str:
    return (
        "🎙 <b>USER JOINED VOICE CHAT</b>\n"
        f"👤 <b>USER:</b> {user_name}\n"
        f"👥 <b>GROUP:</b> {group_title}\n"
        "🌙 🧿"
    )


def _format_vc_join_buttons(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    clean_id = str(chat_id).replace("-100", "")
    vc_link = f"https://t.me/c/{clean_id}/1?videochat"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎧 Join VC", url=vc_link),
                InlineKeyboardButton("➕ Add Me", url=f"tg://user?id={user_id}"),
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
    global _last_vc_chat_id

    if getattr(update, "chat_id", None):
        cid = _normalize_channel_chat_id(update.chat_id)
        if cid:
            _last_vc_chat_id = cid
            return cid

    peer = getattr(update, "peer", None)
    if peer:
        if getattr(peer, "channel_id", None):
            cid = _normalize_channel_chat_id(peer.channel_id)
            if cid:
                _last_vc_chat_id = cid
                return cid
        if getattr(peer, "chat_id", None):
            cid = -abs(int(peer.chat_id))
            _last_vc_chat_id = cid
            return cid

    if chats:
        for chat_key, chat_obj in chats.items():
            raw_id = getattr(chat_obj, "id", None) or chat_key
            cid = _normalize_channel_chat_id(raw_id)
            if cid:
                _last_vc_chat_id = cid
                return cid

    return _last_vc_chat_id


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        global _last_vc_chat_id

        if isinstance(update, types.UpdateGroupCall):
            cid = _extract_chat_id(update, chats)
            if cid:
                _last_vc_chat_id = cid
            return

        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        chat_id = _extract_chat_id(update, chats)
        if not chat_id:
            print("[VC DEBUG] chat_id still None")
            return

        for participant in getattr(update, "participants", []):
            if getattr(participant, "left", False):
                continue

            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            if not user_id:
                continue

            user_name = None
            if user_id in users:
                u = users[user_id]
                first = getattr(u, "first_name", "") or ""
                last = f" {getattr(u, 'last_name', '')}" if getattr(u, "last_name", None) else ""
                user_name = f"{first}{last}".strip()

            if not user_name:
                try:
                    tg_user = await client.get_users(user_id)
                    first = tg_user.first_name or ""
                    last = f" {tg_user.last_name}" if tg_user.last_name else ""
                    user_name = f"{first}{last}".strip()
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

            text = _format_vc_join_text(user_name, group_title)
            reply_markup = _format_vc_join_buttons(chat_id, user_id)

            try:
                await main_bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                print(f"[VC DEBUG] Alert sent in {chat_id} for {user_id}")
            except Exception as exc:
                print(f"[VC DEBUG] Send error in {chat_id}: {exc}")
