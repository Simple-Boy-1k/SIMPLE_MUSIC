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
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union, Optional
import random
import asyncio
import os
import time
from logging import getLogger
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode, ChatMemberStatus
from SIMPLE_MUSIC.utils.database import add_served_chat, get_assistant, is_active_chat
from SIMPLE_MUSIC.misc import SUDOERS
from SIMPLE_MUSIC.mongo.afkdb import PROCESS
from SIMPLE_MUSIC.utils.Simple_ban import admin_filter

LOGGER = getLogger(__name__)

# ❗ APNI WELCOME VIDEO KI TELEGRAM LINK YAHAN PASTE KAREIN ❗
WELCOME_VIDEO_URL = "https://files.catbox.moe/9iom66.mp4" 

# --------------------------------------------------------------------------------- #
class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "on"}  # Default state is "on"

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


@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        A = await wlcm.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        if state == "off":
            if A:
                await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀ─ᴅʏ ᴅɪsᴀʙʟᴇᴅ !**")
            else:
                await wlcm.add_wlcm(chat_id)
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɪɴ** {message.chat.title}")
        elif state == "on":
            if not A:
                await message.reply_text("**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.**")
            else:
                await wlcm.rm_wlcm(chat_id)
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɪɴ** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ!**")


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    group_name = member.chat.title  # Group ka naam nikalne ke liye
    count = await app.get_chat_members_count(chat_id)
    A = await wlcm.find_one(chat_id)
    if A:
        return

    if member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != "kicked":
        user = member.new_chat_member.user

        try:
            button_text = "✙ ᴋɪᴅɴᴀᴘ ᴍᴇ ✙"
            add_link = f"https://t.me/{app.username}?startgroup=true"

            # 📝 Aapka bataya hua custom text format + Group name configuration:
            caption_text = f"""
**⎊─────☵ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ☵─────⎊**
⧽** {group_name}
**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**
☉ **ɴᴀᴍᴇ ⧽** {user.mention}
☉ **ɪᴅ ⧽** `{user.id}`
☉ **ᴜ_ɴᴀᴍᴇ ⧽** @{user.username if user.username else 'None'}
☉ **ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs ⧽** {count}

**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**

**⎉──────▢✭ 侖 ✭▢──────⎉**
"""

            # 🎬 Video ke sath aapka custom text caption bhejega aur ye permanent rahega
            await app.send_video(
                chat_id,
                video=WELCOME_VIDEO_URL,
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=button_text, url=add_link)],
                ])
            )

        except Exception as e:
            LOGGER.error(e)
