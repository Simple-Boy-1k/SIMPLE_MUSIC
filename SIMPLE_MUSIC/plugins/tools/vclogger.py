import asyncio
from pyrogram import filters
from pyrogram.raw import types as raw_types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

try:
    from SIMPLE_MUSIC import app
except Exception:
    app = None

AUTO_DELETE_SECONDS = 20


def get_add_to_group_url(bot_username: str) -> str:
    clean_username = (bot_username or "").lstrip("@")
    admin_perms = (
        "can_manage_chat+can_delete_messages+can_restrict_members+"
        "can_invite_users+can_pin_messages+can_manage_video_chats+"
        "can_promote_members+can_change_info"
    )
    return f"https://t.me/{clean_username}?startgroup=true&admin={admin_perms}"


def build_join_vc_button(add_url: str) -> InlineKeyboardButton:
    try:
        return InlineKeyboardButton(
            text="join vc",
            url=add_url,
            style="danger",
        )
    except TypeError:
        return InlineKeyboardButton(
            text="join vc",
            url=add_url,
        )


async def _delete_after_delay(msg, delay: int = AUTO_DELETE_SECONDS):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


def _normalize_chat_id(raw_chat_id) -> int:
    s = str(raw_chat_id)
    if s.startswith("-100"):
        return int(s)
    return int(f"-100{abs(int(raw_chat_id))}")


async def _send_temp_alert(client, chat_id: int, text: str):
    try:
        me = await client.get_me()
        add_url = get_add_to_group_url(me.username)
        keyboard = InlineKeyboardMarkup([[build_join_vc_button(add_url)]])
        sent_msg = await client.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )
        asyncio.create_task(_delete_after_delay(sent_msg, AUTO_DELETE_SECONDS))
    except Exception:
        pass


if app is not None:

    # 1. VC Start & VC End service messages
    @app.on_message(filters.video_chat_started | filters.video_chat_ended)
    async def vc_status_handler(client, message: Message):
        chat_id = message.chat.id
        if message.video_chat_started:
            text = (
                "🎙 **Voice Chat Started!**\n\n"
                f"📌 **Group:** {message.chat.title or chat_id}\n\n"
                f"⏳ *Ye message {AUTO_DELETE_SECONDS}s mein delete ho jayega.*"
            )
        else:
            text = (
                "📴 **Voice Chat Ended!**\n\n"
                f"📌 **Group:** {message.chat.title or chat_id}\n\n"
                f"⏳ *Ye message {AUTO_DELETE_SECONDS}s mein delete ho jayega.*"
            )
        await _send_temp_alert(client, chat_id, text)

    # 2. VC Join & VC Leave participant updates
    @app.on_raw_update()
    async def vc_participant_handler(client, update, users, chats):
        if not isinstance(update, raw_types.UpdateGroupCallParticipants):
            return

        chat_id = _normalize_chat_id(update.chat_id)

        if not hasattr(client, "_vc_active_users"):
            client._vc_active_users = set()

        for participant in update.participants:
            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            if not user_id:
                continue

            is_left = bool(getattr(participant, "left", False))
            was_in_vc = (chat_id, user_id) in client._vc_active_users

            if is_left:
                if not was_in_vc:
                    continue
                client._vc_active_users.discard((chat_id, user_id))
                event_title = "🚪 **Voice Chat Leave Alert!**"
            else:
                if was_in_vc:
                    continue
                client._vc_active_users.add((chat_id, user_id))
                event_title = "🎙 **Voice Chat Join Alert!**"

            try:
                user = await client.get_users(user_id)
            except Exception:
                continue

            full_name = (
                f"{user.first_name or ''} {user.last_name or ''}".strip()
                or "Unknown User"
            )
            username_text = f"@{user.username}" if user.username else "No Username"

            text = (
                f"{event_title}\n\n"
                f"👤 **Name:** {full_name}\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"🔗 **Username:** {username_text}\n\n"
                f"⏳ *Ye message {AUTO_DELETE_SECONDS}s mein delete ho jayega.*"
            )
            await _send_temp_alert(client, chat_id, text)
