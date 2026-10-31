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
        self.data = set()

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
# WELCOME NEW MEMBERS (DISABLED PERMANENTLY AS REQUESTED)
# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    # Ab koi bhi naya member aayega toh welcome nahi hoga
    return
