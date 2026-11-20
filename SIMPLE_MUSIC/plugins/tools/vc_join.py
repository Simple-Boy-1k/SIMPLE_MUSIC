import asyncio
from pyrogram.raw import types as raw_types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

try:
    from SIMPLE_MUSIC import app
except Exception:
    app = None

AUTO_DELETE_SECONDS = 20
_VC_ACTIVE_USERS = set()


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


if app is not None:

    @app.on_raw_update()
    async def vc_join_handler(client, update, users, chats):
        try:
            vc_updates = _extract_vc_participant_updates(update)
            if not vc_updates:
                return

            me = await client.get_me()
            add_url = get_add_to_group_url(getattr(me, "username", "") or "")
            keyboard = InlineKeyboardMarkup([[build_join_vc_button(add_url)]])

            for vc_upd in vc_updates:
                chat_id = _resolve_chat_id(vc_upd.chat_id, chats or {})

                for participant in vc_upd.participants:
                    peer = getattr(participant, "peer", None)
                    user_id = getattr(peer, "user_id", None)
                    if not user_id:
                        continue
                    user_id = int(user_id)

                    is_left = bool(getattr(participant, "left", False))
                    was_in_vc = (chat_id, user_id) in _VC_ACTIVE_USERS

                    if is_left:
                        if not was_in_vc:
                            continue
                        _VC_ACTIVE_USERS.discard((chat_id, user_id))
                        event_title = "🚪 **Voice Chat Leave Alert!**"
                    else:
                        if was_in_vc:
                            continue
                        _VC_ACTIVE_USERS.add((chat_id, user_id))
                        event_title = "🎙 **Voice Chat Join Alert!**"

                    full_name = "Unknown User"
                    username_text = "No Username"

                    if users and user_id in users:
                        u = users[user_id]
                        fn = getattr(u, "first_name", "") or ""
                        ln = getattr(u, "last_name", "") or ""
                        if f"{fn} {ln}".strip():
                            full_name = f"{fn} {ln}".strip()
                        if getattr(u, "username", None):
                            username_text = f"@{u.username}"

                    if full_name == "Unknown User":
                        try:
                            user = await client.get_users(user_id)
                            full_name = (
                                f"{user.first_name or ''} {user.last_name or ''}".strip()
                                or "Unknown User"
                            )
                            username_text = (
                                f"@{user.username}" if user.username else "No Username"
                            )
                        except Exception:
                            pass

                    text = (
                        f"{event_title}\n\n"
                        f"👤 **Name:** {full_name}\n"
                        f"🆔 **ID:** `{user_id}`\n"
                        f"🔗 **Username:** {username_text}\n\n"
                        f"⏳ *यह मैसेज {AUTO_DELETE_SECONDS}s में डिलीट हो जाएगा।*"
                    )

                    sent_msg = await client.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=keyboard,
                    )
                    asyncio.create_task(
                        _delete_after_delay(sent_msg, AUTO_DELETE_SECONDS)
                    )
        except Exception:
            pass
