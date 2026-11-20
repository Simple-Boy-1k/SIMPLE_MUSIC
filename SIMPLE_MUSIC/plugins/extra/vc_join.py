from pyrogram import Client
from pyrogram.raw import types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _format_vc_join_text(user_name: str, group_title: str) -> str:
    return (
        "🎙 <b>USER JOINED VOICE CHAT</b>\n"
        f"👤 <b>USER:</b> {user_name}\n"
        f"👥 <b>GROUP:</b> {group_title}\n"
        ""
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


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        chat_id = None
        if getattr(update, "chat_id", None):
            chat_id = int(f"-100{update.chat_id}")
        elif getattr(update, "peer", None) and getattr(update.peer, "channel_id", None):
            chat_id = int(f"-100{update.peer.channel_id}")

        if not chat_id:
            return

        for participant in getattr(update, "participants", []):
            is_joined = (
                getattr(participant, "just_joined", False)
                or getattr(participant, "date", None) is not None
            ) and not getattr(participant, "left", False)

            if not is_joined:
                continue

            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            if not user_id or user_id not in users:
                continue

            user = users[user_id]
            first_name = user.first_name or ""
            last_name = f" {user.last_name}" if user.last_name else ""
            user_name = f"{first_name}{last_name}".strip() or f"User {user_id}"

            group_title = "Group"
            if chat_id in chats:
                group_title = getattr(chats[chat_id], "title", group_title)
            else:
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
            except Exception as exc:
                print(f"[VC Notifier] Failed in {chat_id}: {exc}")
