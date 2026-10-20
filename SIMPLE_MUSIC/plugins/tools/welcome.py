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
OWNER_USERNAME = "Simple_Boy_1k"


# --------------------------------------------------------------------------------- #
class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "off"}

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]


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
    enabled = await wlcm.find_one(chat_id)

    if state == "off":
        if enabled:
            await wlcm.rm_wlcm(chat_id)

        await message.reply_text(
            f"**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**"
        )

    elif state == "on":
        if enabled:
            await message.reply_text(
                "**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**"
            )
        else:
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

    # Welcome disabled check
    if await wlcm.find_one(chat_id):
        return

    # Check for a new member
    if not member.new_chat_member:
        return

    if member.new_chat_member.status in (
        enums.ChatMemberStatus.BANNED,
        enums.ChatMemberStatus.LEFT,
    ):
        return

    user = member.new_chat_member.user

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

        # Welcome caption — screenshot-inspired small font
        caption_text = f"""
「 ᴡ ᴇ ʟ ᴄ ᴏ ᴍ ᴇ  ʙ ᴀ ʙ ʏ 」〞

│
├──「 ɴ ᴀ ᴍ ᴇ 」 ➜ {user.first_name}
│
├──「 ᴜ s ᴇ ʀ 」 ➜ {username}
│
├──「 ɢ ʀ ᴏ ᴜ ᴘ 」 ➜ {group_name}
│
├──「 ᴍ ᴇ ᴍ ʙ ᴇ ʀ s 」 ➜ {count}
│
├──「 ɢ ʀ ᴏ ᴜ ᴘ  ʀ ᴜ ʟ ᴇ s 」
│
├── ʀ ᴇ s ᴘ ᴇ ᴄ ᴛ  ᴀ ʟ ʟ  ᴍ ᴇ ᴍ ʙ ᴇ ʀ s .
├── ɴ ᴏ  s ᴘ ᴀ ᴍ  ᴏ ʀ  18+  ᴄ ᴏ ɴ ᴛ ᴇ ɴ ᴛ .
├── ᴇ ɴ ᴊ ᴏ ʏ  ᴛ ʜ ᴇ  ᴍ ᴜ s ɪ ᴄ  ᴀ ɴ ᴅ  ᴠ ɪ ʙ ᴇ !
│
└──「 ᴘ ᴏ ᴡ ᴇ ʀ ᴇ ᴅ  ʙ ʏ  @Simple_Boy_1k 」
"""

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
        await app.send_video(
            chat_id=chat_id,
            video=WELCOME_VIDEO_URL,
            caption=caption_text,
            reply_markup=buttons,
        )

    except Exception:
        LOGGER.exception(
            "Welcome message failed in chat %s",
            chat_id,
        )
