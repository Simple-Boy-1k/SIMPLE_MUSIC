# -----------------------------------------------
# 🔸 SIMPLE MUSIC Project
# 🔹 Developed & Maintained by: Simple Boy (https://github.com/Simple-Boy-1k)
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
import random
from typing import Union
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SIMPLE_MUSIC import app
import config

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def _get_style(style_val):
    if getattr(config, "BUTTON_COLOUR", False):
        return {"style": style_val}
    return {}

# Chat-wise autoplay status store karne ke liye dictionary
autoplay_status = {}

def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    r1, r2 = random.choices(STYLES, k=2)
    not_dur = [
        [
            InlineKeyboardButton(
                text="ǫᴜᴇᴜᴇ",
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                **_get_style(r1)
            ),
            InlineKeyboardButton(
                text="ᴄʟᴏꜱᴇ",
                callback_data="close",
                **_get_style(r1)
            ),
        ]
    ]
    dur_list = [
        [
            InlineKeyboardButton(
                text=f"{played} / {dur}",
                callback_data="GetTimer",
                **_get_style(r1)
            )
        ],
        [
            InlineKeyboardButton(
                text="ǫᴜᴇᴜᴇ",
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                **_get_style(r2)
            ),
            InlineKeyboardButton(
                text="ᴄʟᴏꜱᴇ",
                callback_data="close",
                **_get_style(r2)
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur_list)
    return upl


def queue_back_markup(_, CPLAY):
    r1 = random.choice(STYLES)
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="ʙᴀᴄᴋ",
                    callback_data=f"queue_back_timer {CPLAY}",
                    **_get_style(r1)
                ),
                InlineKeyboardButton(
                    text="ᴄʟᴏꜱᴇ",
                    callback_data="close",
                    **_get_style(r1)
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    r1, r2, r3, r4 = random.choices(STYLES, k=4)
    # Autoplay status check karke stylish ENABLED ya DISABLED dikhane ke liye
    is_autoplay = autoplay_status.get(chat_id, True)
    autoplay_text = "ᴀᴜᴛᴏᴘʟᴀʏ : ᴇɴᴀʙʟᴇᴅ" if is_autoplay else "ᴀᴜᴛᴏᴘʟᴀʏ : ᴅɪꜱᴀʙʟᴇᴅ"
    
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", 
                url=f"https://t.me/{app.username}?startgroup=true",
                **_get_style(r1)
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", **_get_style(r2)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", **_get_style(r2)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", **_get_style(r2)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", **_get_style(r2)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", **_get_style(r2)),
        ],
        [
            InlineKeyboardButton(text=autoplay_text, callback_data=f"AutoplayToggle {chat_id}", **_get_style(r3)),
        ],
        [InlineKeyboardButton(text="ᴄʟᴏꜱᴇ", callback_data="close", **_get_style(r4))],
    ]
    return buttons
