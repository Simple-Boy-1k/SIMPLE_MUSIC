import asyncio
from pyrogram.raw import types as raw_types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

try:
    from SIMPLE_MUSIC import app
except Exception:
    app = None

AUTO_DELETE_SECONDS = 20
_VC_ACTIVE = set()
_BOT_USERNAME = None


def _add_url(username: str) -> str:
    clean = (username or "").lstrip("@")
    perms = (
        "can_manage_chat+can_delete_messages+can_restrict_members+"
        "can_invite_users+can_pin_messages+can_manage_video_chats+"
        "can_promote_members+can_change_info"
    )
    return f"https://t.me/{clean}?startgroup=true&admin={perms}"


def _vc_button(url: str) -> InlineKeyboardButton:
    try:
        return InlineKeyboardButton(text="join vc", url=url, style="danger")
    except TypeError:
        return InlineKeyboardButton(text="join vc", url=url)


async def _auto_delete(msg):
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    try:
        await msg.delete()
    except Exception:
        pass


def _to_chat_id(raw_id, chats: dict) -> int:
    if chats and raw_id in chats:
        cid = getattr(chats[raw_id], "id", None)
        if cid:
            raw_id = cid
    s = str(raw_id)
    if s.startswith("-100"):
        return int(s)
    return int(f"-100{abs(int(raw_id))}")


def _pull_updates(update):
    out = []
    if isinstance(update, raw_types.UpdateGroupCallParticipants):
        out.append(update)
    elif isinstance(update, (raw_types.Updates, raw_types.UpdateCombined)):
        for item in getattr(update, "updates", []) or []:
            if isinstance(item, raw_types.UpdateGroupCallParticipants):
                out.append(item)
    elif isinstance(update, raw_types.UpdateShort):
        sub = getattr(update, "update", None)
        if isinstance(sub, raw_types.UpdateGroupCallParticipants):
            out.append(sub)
    return out


if app is not None:

    @app.on_raw_update()
    async def on_vc_join(client, update, users, chats):
        global _BOT_USERNAME
        try:
            items = _pull_updates(update)
            if not items:
                return

            if not _BOT_USERNAME:
                me = await client.get_me()
                _BOT_USERNAME = getattr(me, "username", "") or ""

            kb = InlineKeyboardMarkup([[_vc_button(_add_url(_BOT_USERNAME))]])

            for upd in items:
                chat_id = _to_chat_id(upd.chat_id, chats or {})

                for p in upd.participants:
                    peer = getattr(p, "peer", None)
                    uid = getattr(peer, "user_id", None)
                    if not uid:
                        continue
                    uid = int(uid)

                    if getattr(p, "left", False):
                        _VC_ACTIVE.discard((chat_id, uid))
                        continue

                    if (chat_id, uid) in _VC_ACTIVE:
                        continue
                    _VC_ACTIVE.add((chat_id, uid))

                    name = "Unknown User"
                    uname = "No Username"

                    if users and uid in users:
                        u = users[uid]
                        full = f"{getattr(u, 'first_name', '') or ''} {getattr(u, 'last_name', '') or ''}".strip()
                        if full:
                            name = full
                        if getattr(u, "username", None):
                            uname = f"@{u.username}"

                    if name == "Unknown User":
                        try:
                            u = await client.get_users(uid)
                            full = f"{u.first_name or ''} {u.last_name or ''}".strip()
                            if full:
                                name = full
                            uname = f"@{u.username}" if u.username else "No Username"
                        except Exception:
                            pass

                    text = (
                        "🎙 **VC Join Alert!**\n\n"
                        f"👤 **Name:** {name}\n"
                        f"🆔 **ID:** `{uid}`\n"
                        f"🔗 **Username:** {uname}\n\n"
                        f"⏳ *{AUTO_DELETE_SECONDS}s mein delete ho jayega.*"
                    )

                    msg = await client.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=kb,
                    )
                    asyncio.create_task(_auto_delete(msg))
        except Exception:
            pass
