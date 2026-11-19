# -----------------------------------------------
# 🔸 SIMPLE MUSIC Project
# 🔹 Developed & Maintained by: Simple (https://github.com/Simple-Boy-1k)
# 📅 Copyright © 2026 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by Simple_Boy_1k
# -----------------------------------------------

from SIMPLE_MUSIC import app
from pyrogram.errors import RPCError
from pyrogram.types import (
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from typing import Union, Optional
import random
import asyncio
import os
import time
from logging import getLogger
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode, ChatMemberStatus
from SIMPLE_MUSIC.utils.database import (
    add_served_chat,
    get_assistant,
    is_active_chat,
)
from SIMPLE_MUSIC.misc import SUDOERS
from SIMPLE_MUSIC.mongo.afkdb import PROCESS
from SIMPLE_MUSIC.utils.Simple_ban import admin_filter

LOGGER = getLogger(__name__)

# ❗ WELCOME VIDEO URL ❗
WELCOME_VIDEO_URL = "https://files.catbox.moe/9iom66.mp4"

# OWNER CONFIGURATION
OWNER_USERNAME = "Sarkar_owner1k"

# ⏱️ AUTO DELETE TIME (IN SECONDS)
AUTO_DELETE_SECONDS = 10

# 🌟 PREMIUM EMOJI IDs CONFIGURATION (Apni Custom/Premium Emoji IDs yahan daalein)
# Example: "sparkle": "5368324170671202286"
EMOJI_IDS = {
    "sparkle": "5235452773184589497",   # ✨ ke liye premium emoji ID
    "user": "5256143829672672750",      # 👤 ke liye premium emoji ID
    "link": "5870998024779468554",      # 🔗 ke liye premium emoji ID
    "id": "5429571366384842791",        # 🆔 ke liye premium emoji ID
    "home": "5841494459904168607",      # 🏠 ke liye premium emoji ID
    "members": "5258513401784573443",   # 👥 ke liye premium emoji ID
    "rules": "5348178055338671586",     # 📜 ke liye premium emoji ID
    "bolt": "5346136537123801643",      # ⚡ ke liye premium emoji ID
}


def p_emoji(key: str, fallback: str) -> str:
    """Agar EMOJI_IDS[key] mein ID dali hai toh <emoji id='...'>fallback</emoji> return karega."""
    emoji_id = str(EMOJI_IDS.get(key, "")).strip()
    if emoji_id:
        return f'<emoji id="{emoji_id}">{fallback}</emoji>'
    return fallback


async def _auto_delete_message(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


# --------------------------------------------------------------------------------- #
class WelDatabase:
    def __init__(self):
        self.data = set()  # Disabled chats ko store karne ke liye set use kiya hai

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id in self.data:
            self.data.remove(chat_id)

    async def rm_wlcm(self, chat_id):
        self.data.add(chat_id)


wlcm = WelDatabase()


class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


# --------------------------------------------------------------------------------- #
# WELCOME ON / OFF COMMAND
# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**"

    if len(message.command) == 1:
        return await message.reply_text(usage)

    if not message.from_user:
        return

    chat_id = message.chat.id

    try:
        user = await app.get_chat_member(
            chat_id,
            message.from_user.id,
        )
    except RPCError:
        return await message.reply_text(
            "Unable to verify your admin status."
        )

    if user.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        return await message.reply_text(
            "**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢs!**"
        )

    state = message.text.split(None, 1)[1].strip().lower()
    disabled = await wlcm.find_one(chat_id)

    if state == "off":
        if disabled:
            return await message.reply_text(
                f"**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**"
            )

        await wlcm.rm_wlcm(chat_id)
        await message.reply_text(
            f"**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**"
        )

    elif state == "on":
        if not disabled:
            return await message.reply_text(
                "**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**"
            )

        await wlcm.add_wlcm(chat_id)
        await message.reply_text(
            f"**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**"
        )

    else:
        await message.reply_text(usage)


# --------------------------------------------------------------------------------- #
# WELCOME NEW MEMBERS
# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    group_name = member.chat.title or "Unknown Group"

    # Agar welcome disabled hai is chat mein, toh yahin rok do
    if await wlcm.find_one(chat_id):
        return

    # Check if there is a new chat member update
    if not member.new_chat_member:
        return

    # Purane member ka status change hone par welcome trigger na ho
    old_status = member.old_chat_member.status if member.old_chat_member else None
    if old_status not in (None, ChatMemberStatus.BANNED, ChatMemberStatus.LEFT):
        return

    new_status = member.new_chat_member.status
    if new_status not in (
        enums.ChatMemberStatus.MEMBER,
        enums.ChatMemberStatus.OWNER,
    ) and old_status is not None:
        return

    user = member.new_chat_member.user

    # Bot accounts ko skip karein
    if user.is_bot:
        return

    try:
        # Bot details
        bot = await app.get_me()

        # Total members
        count = await app.get_chat_members_count(chat_id)

        # Username
        username = (
            f"@{user.username}"
            if user.username
            else "Not Set"
        )

        e_sparkle = p_emoji("sparkle", "✨")
        e_user = p_emoji("user", "👤")
        e_link = p_emoji("link", "🔗")
        e_id = p_emoji("id", "🆔")
        e_home = p_emoji("home", "🏠")
        e_members = p_emoji("members", "👥")
        e_rules = p_emoji("rules", "📜")
        e_bolt = p_emoji("bolt", "⚡")

        # Welcome caption (HTML parse mode ke saath blockquote + premium emoji tags)
        caption_text = f"""<blockquote>
{e_sparkle} 𝙒 𝙀 𝙇 𝘾 𝙊 𝙈 𝙀   𝘽 𝘼 𝘽 𝙔 {e_sparkle}

├─ {e_user} ➜ {user.first_name}
│
├─ {e_link} ➜ {username}
│
├─ {e_id}  ➜ <code>{user.id}</code>
│
├─ {e_home} ➜ {group_name}
│
├─ {e_members} ➜ {count}
│
└─ {e_bolt}{e_bolt}</blockquote>"""

        # Inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✙ ᴋɪᴅɴᴀᴘ ᴍᴇ ✙",
                        url=f"https://t.me/{bot.username}?startgroup=true",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ᴍᴀsᴛᴇʀ (ᴏᴡɴᴇʀ)",
                        url=f"https://t.me/{OWNER_USERNAME}",
                    )
                ],
            ]
        )

        # Send welcome video with caption and buttons
        sent_msg = await app.send_video(
            chat_id=chat_id,
            video=WELCOME_VIDEO_URL,
            caption=caption_text,
            parse_mode=ParseMode.HTML,
            reply_markup=buttons,
        )

        # 10 seconds baad auto-delete
        if sent_msg:
            asyncio.create_task(_auto_delete_message(sent_msg, AUTO_DELETE_SECONDS))

    except Exception:
        LOGGER.exception(
            "Welcome message failed in chat %s",
            chat_id,
        )
