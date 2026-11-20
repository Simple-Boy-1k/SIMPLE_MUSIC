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
        print(f"[VC DEBUG] Subscribed group call in chat_id={chat_id}")
    except Exception as e:
        print(f"[VC DEBUG] Subscribe failed for {chat_id}: {e}")


async def _subscribe_existing_calls(client: Client):
    try:
        async for dialog in client.get_dialogs():
            chat = getattr(dialog, "chat", None)
            if not chat:
                continue
            chat_type = str(getattr(chat, "type", "")).lower()
            if "supergroup" in chat_type or "channel" in chat_type:
                await subscribe_group_call(client, chat.id)
                await asyncio.sleep(0.2)
    except Exception as e:
        print(f"[VC DEBUG] Dialog scan error: {e}")


def attach_vc_join_notifier(assistant_client: Client, main_bot: Client):
    print(f"[VC DEBUG] Attached notifier to assistant={getattr(assistant_client, 'name', assistant_client)}")

    @assistant_client.on_raw_update()
    async def _on_vc_join_raw_update(client: Client, update, users: dict, chats: dict):
        if isinstance(update, types.UpdateGroupCall):
            chat_id = _extract_chat_id(update)
            print(f"[VC DEBUG] UpdateGroupCall in chat_id={chat_id}")
            if chat_id:
                await subscribe_group_call(client, chat_id)
            return

        if not isinstance(update, types.UpdateGroupCallParticipants):
            return

        chat_id = _extract_chat_id(update)
        participants = getattr(update, "participants", [])
        print(f"[VC DEBUG] UpdateGroupCallParticipants in chat_id={chat_id}, count={len(participants)}")

        if not chat_id:
            return

        for participant in participants:
            left = getattr(participant, "left", False)
            peer = getattr(participant, "peer", None)
            user_id = getattr(peer, "user_id", None)
            print(f"[VC DEBUG] Participant user_id={user_id}, left={left}")

            if left or not user_id:
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
                except Exception as e:
                    print(f"[VC DEBUG] get_users error for {user_id}: {e}")

            user_name = user_name or f"User {user_id}"

            group_title = "Group"
            if chat_id in chats:
                group_title = getattr(chats[chat_id], "title", group_title) or group_title
            else:
                try:
                    chat_obj = await client.get_chat(chat_id)
                    group_title = chat_obj.title or group_title
                except Exception as e:
                    print(f"[VC DEBUG] get_chat error for {chat_id}: {e}")

            text = _format_vc_join_text(user_name, group_title)
            reply_markup = _format_vc_join_buttons(chat_id, user_id)

            try:
                await main_bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                print(f"[VC DEBUG] Alert sent successfully to {chat_id} for user {user_id}")
            except Exception as exc:
                print(f"[VC DEBUG] Failed sending message in {chat_id}: {exc}")

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_subscribe_existing_calls(assistant_client))
    except RuntimeError:
        pass
