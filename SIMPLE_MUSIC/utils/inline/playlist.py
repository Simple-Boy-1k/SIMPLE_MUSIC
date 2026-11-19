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
import config
import random
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def get_random_style():
    if getattr(config, "BUTTON_COLOUR", False):
        return {"style": random.choice(STYLES)}
    return {}

def botplaylist_markup(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["PL_B_1"],
                callback_data="get_playlist_playmode",
                **get_random_style()
            ),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", **get_random_style()),
        ],
    ]
    return buttons


def top_play_markup(_):
    buttons = [
        [InlineKeyboardButton(text=_["PL_B_9"], callback_data="SERVERTOP global", **get_random_style())],
        [InlineKeyboardButton(text=_["PL_B_10"], callback_data="SERVERTOP chat", **get_random_style())],
        [InlineKeyboardButton(text=_["PL_B_11"], callback_data="SERVERTOP user", **get_random_style())],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="get_playmarkup", **get_random_style()),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", **get_random_style()),
        ],
    ]
    return buttons


def get_playlist_markup(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data="play_playlist a", **get_random_style()),
            InlineKeyboardButton(text=_["P_B_2"], callback_data="play_playlist v", **get_random_style()),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="home_play", **get_random_style()),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", **get_random_style()),
        ],
    ]
    return buttons


def top_play_markup(_):
    buttons = [
        [InlineKeyboardButton(text=_["PL_B_9"], callback_data="SERVERTOP Global", **get_random_style())],
        [InlineKeyboardButton(text=_["PL_B_10"], callback_data="SERVERTOP Group", **get_random_style())],
        [InlineKeyboardButton(text=_["PL_B_11"], callback_data="SERVERTOP Personal", **get_random_style())],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="get_playmarkup", **get_random_style()),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", **get_random_style()),
        ],
    ]
    return buttons


def failed_top_markup(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="get_top_playlists",
                **get_random_style()
            ),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", **get_random_style()),
        ],
    ]
    return buttons


def warning_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["PL_B_7"],
                    callback_data="delete_whole_playlist",
                    **get_random_style()
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="del_back_playlist",
                    **get_random_style()
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    **get_random_style()
                ),
            ],
        ]
    )
    return upl


def close_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    **get_random_style()
                ),
            ]
        ]
    )
    return upl
    
