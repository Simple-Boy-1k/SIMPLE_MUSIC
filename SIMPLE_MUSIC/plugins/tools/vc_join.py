import asyncio
from pyrogram.raw import functions as raw_functions
from pyrogram.raw import types as raw_types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

AUTO_DELETE_SECONDS = 20

clients = []
try:
    from SIMPLE_MUSIC import app
    if app is not None:
        clients.append(app)
except Exception as e:
    print(f"[VC_JOIN] app import err: {e}")

for mod_path, attr_name in [
    ("SIMPLE_MUSIC.core.userbot", "userbot"),
    ("SIMPLE_MUSIC.core.userbot", "ub"),
    ("SIMPLE_MUSIC", "userbot"),
]:
    try:
        mod = __import__(mod_path, fromlist=[attr_name])
        obj = getattr(mod, attr_name, None)
        if isinstance(obj, list):
            for item in obj:
                if item is not None and item not in clients:
                    clients.append(item)
        elif obj is not None and obj not in clients:
            clients.append(obj)
    except Exception:
        pass


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


def _normalize_supergroup_id(raw_id) -> int:
    s = str(raw_id)
    if s.startswith("-100"):
        return int(s)
    return int(f"-100{abs(int(raw_id))}")


def _resolve_chat_id(raw_chat_id, chats: dict) -> int:
    if chats and raw_chat_id in chats:
        chat_obj = chats[raw_chat_id]
        cid = getattr(chat_obj, "id", None)
        if cid:
            return _normalize_supergroup_id(cid)
    return _normalize_supergroup_id(raw_chat_id)


def _extract_user_id(peer) -> int | None:
    if peer is None:
        return None
    uid = getattr(peer, "user_id", None)
    return int(uid) if uid else None


def _extract_vc_participant_updates(update):
    found = []
    if isinstance(update, raw_types.UpdateGroupCallParticipants):
        found.append(update)
    elif isinstance(update, (raw_types.Updates, raw_types.UpdateCombined)):
        for sub in getattr(update, "updates", []) or []:
            if isinstance(sub, raw_types.UpdateGroupCallParticipants):
                found.append(sub)
    elif isinstance(update, raw_types.UpdateShort):
        sub = getattr(update, "update", None)
        if isinstance(sub, raw_types.UpdateGroupCallParticipants):
            found.append(sub)
    return found


async def _subscribe_call(client, chat_id: int, update_obj):
    call_obj = getattr(update_obj, "call", None)
    if not isinstance(call_obj, raw_types.InputGroupCall):
        return
    if not hasattr(client, "_vc_subscribed"):
        client._vc_subscribed = set()
    key = (id(client), call_obj.id)
    if key in client._vc_subscribed:
        return
    client._vc_subscribed.add(key)
    try:
        await client.invoke(
            raw_functions.phone.GetGroupParticipants(
                call=call_obj,
                ids=[],
                sources=[],
                offset="",
                limit=50,
            )
        )
    except Exception:
        pass


async def _get_bot_username(fallback_client) -> str:
    for c in clients:
        try:
            me = await c.get_me()
            if me and me.username:
                return me.username
        except Exception:
            pass
    try:
        me = await fallback_client.get_me()
        return me.username or ""
    except Exception:
        return ""


async def _get_user_info(client, user_id: int, users_map: dict):
    full_name = None
    username_text = None

    if users_map and user_id in users_map:
        u = users_map[user_id]
        fn = getattr(u, "first_name", "") or ""
        ln = getattr(u, "last_name", "") or ""
        combined = f"{fn} {ln}".strip()
        if combined:
            full_name = combined
        uname = getattr(u, "username", None)
        if uname:
            username_text = f"@{uname}"

    if not full_name or not username_text:
        for c in ([client] + [x for x in clients if x is not client]):
            try:
                user = await c.get_users(user_id)
                if not full_name:
                    full_name = (
                        f"{user.first_name or ''} {user.last_name or ''}".strip()
                        or "Unknown User"
                    )
                if not username_text:
                    username_text = (
                        f"@{user.username}" if user.username else "No Username"
                    )
                break
            except Exception:
                continue

    return full_name or "Unknown User", username_text or "No Username"


def register_vc_handler(target_client):
    @target_client.on_raw_update()
    async def vc_join_handler(client, update, users, chats):
        if isinstance(update, raw_types.UpdateGroupCall):
            chat_id = _resolve_chat_id(update.chat_id, chats or {})
            await _subscribe_call(client, chat_id, update)
            return

        vc_updates = _extract_vc_participant_updates(update)
        if not vc_updates:
            return

        bot_uname = await _get_bot_username(client)
        add_url = get_add_to_group_url(bot_uname)
        keyboard = InlineKeyboardMarkup([[build_join_vc_button(add_url)]])
        sender = clients[0] if clients else client

        for vc_upd in vc_updates:
            chat_id = _resolve_chat_id(vc_upd.chat_id, chats or {})

            if not hasattr(client, "_vc_active_users"):
                client._vc_active_users = set()

            for participant in vc_upd.participants:
                user_id = _extract_user_id(getattr(participant, "peer", None))
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

                full_name, username_text = await _get_user_info(
                    client, user_id, users or {}
                )

                text = (
                    f"{event_title}\n\n"
                    f"👤 **Name:** {full_name}\n"
                    f"🆔 **ID:** `{user_id}`\n"
                    f"🔗 **Username:** {username_text}\n\n"
                    f"⏳ *Ye message {AUTO_DELETE_SECONDS}s mein delete ho jayega.*"
                )

                try:
                    sent_msg = await sender.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=keyboard,
                    )
                    asyncio.create_task(
                        _delete_after_delay(sent_msg, AUTO_DELETE_SECONDS)
                    )
                except Exception as e:
                    print(f"[VC_JOIN] Send error in {chat_id}: {e}")


for _c in clients:
    register_vc_handler(_c)
