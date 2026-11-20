import asyncio
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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


def _extract_chat_id(update):
    if getattr(update, "chat_id", None):
        return int(f"-100{update.chat_id}")
    peer = getattr(update, "peer", None)
    if peer and getattr(peer, "channel_id", None):
        return int(f"-100{peer.channel_id}")
    if peer and getattr(peer, "chat_id", None):
        return -int(peer.chat_id)
    return None


async def subscribe_group_call(client: Client, chat_id: int):
    """Group ki active VC ke participant updates subscribe karta hai."""
    try:
        peer = await client.resolve_peer(chat_id)
        if not isinstance(peer, types.InputPeerChannel):
            return

        full_chat = await client.invoke(
            functions.channels.GetFullChannel(channel=peer)
        )
        call = getattr(full_chat.full_chat, "call", None)
        if not call:
            return

        input_call = types.InputGroupCall(
            id=call.id,
            access_hash=call.access_hash,
        )
        await client.invoke(
            functions.phone.GetGroupCall(
                call=input_call,
                limit=100,
            )
        )
    except Exception:
        pass


async def _subscribe_existing_calls(client: Client):
    """Bot start hone par assistant ke supergroups/channels ki active VCs subscribe karta hai."""
    try:
        async for dialog in client.get_dialogs():
            chat = getattr(dialog, "chat", None)
            if not chat:
                continue
            chat_type = str(getattr(chat, "type", "")).lower()
            if "supergroup" in chat_type or "channel" in chat_type:
                await subscribe_group_call(client, chat.id)
                await asyncio.sleep(0.2)
    except Exception:
        pass


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        if isinstance(update, types.UpdateGroupCall):
            chat_id = _extract_chat_id(update)
            if chat_id:
                await subscribe_group_call(client, chat_id)
            return

        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        chat_id = _extract_chat_id(update)
        if not chat_id:
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
            if chat_id in chats:
                group_title = getattr(chats[chat_id], "title", group_title) or group_title
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

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_subscribe_existing_calls(assistant_client))
    except RuntimeError:
        pass
