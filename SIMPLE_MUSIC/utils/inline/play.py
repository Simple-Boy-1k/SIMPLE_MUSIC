import math
import random
import config
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.utils.formatters import time_to_seconds

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def _get_style(style_val):
    if getattr(config, "BUTTON_COLOUR", False):
        return {"style": style_val}
    return {}

def track_markup(_, videoid, user_id, channel, fplay):
    r1 = random.choice(STYLES)
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                **_get_style(r1)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                **_get_style(r1)
            ),
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)

    remaining_sec = duration_sec - played_sec
    if remaining_sec < 0:
        remaining_sec = 0

    rem_min = remaining_sec // 60
    rem_sec = remaining_sec % 60
    remaining = f"{rem_min:02d}:{rem_sec:02d}"

    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "|♬—————————|-"
    elif 10 < umm < 20:
        bar = "|—♬————————|-"
    elif 20 <= umm < 30:
        bar = "|——♬———————|-"
    elif 30 <= umm < 40:
        bar = "|———♬——————|-"
    elif 40 <= umm < 50:
        bar = "|————♬—————|-"
    elif 50 <= umm < 60:
        bar = "|—————♬————|-"
    elif 60 <= umm < 70:
        bar = "|——————♬———|-"
    elif 70 <= umm < 80:
        bar = "|———————♬——|-"
    elif 80 <= umm < 95:
        bar = "|指標———————♬—|-"
    else:
        bar = "|—————————♬|-"

    r1, r2, r3 = random.choices(STYLES, k=3)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {remaining}",
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
            InlineKeyboardButton(text="SUPPORT", url=config.SUPPORT_CHAT, **_get_style(r3)),
            InlineKeyboardButton(text="CHANNEL", url=config.SUPPORT_CHANNEL, **_get_style(r3)),
        ],
        [
            InlineKeyboardButton(text="AUTOPLAY SKIP", callback_data=f"AutoplaySkip {chat_id}", **_get_style(r3)),
        ],
        [
            InlineKeyboardButton(text="AUTOPLAY : ON", callback_data=f"AutoplayToggle {chat_id}", **_get_style(r3)),
        ],
    ]
    return buttons


def stream_markup(_, chat_id):
    r1, r2 = random.choices(STYLES, k=2)
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", **_get_style(r1)),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", **_get_style(r1)),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", **_get_style(r1)),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", **_get_style(r1)),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", **_get_style(r1)),
        ],
        [
            InlineKeyboardButton(text="SUPPORT", url=config.SUPPORT_CHAT, **_get_style(r2)),
            InlineKeyboardButton(text="CHANNEL", url=config.SUPPORT_CHANNEL, **_get_style(r2)),
        ],
        [
            InlineKeyboardButton(text="AUTOPLAY SKIP", callback_data=f"AutoplaySkip {chat_id}", **_get_style(r2)),
        ],
        [
            InlineKeyboardButton(text="AUTOPLAY : ON", callback_data=f"AutoplayToggle {chat_id}", **_get_style(r2)),
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    r1 = random.choice(STYLES)
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"SIMPLEPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                **_get_style(r1)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"SIMPLEPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                **_get_style(r1)
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    r1 = random.choice(STYLES)
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                **_get_style(r1)
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    r1, r2 = random.choices(STYLES, k=2)
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                **_get_style(r1)
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                **_get_style(r1)
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                **_get_style(r2)
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                **_get_style(r2)
            ),
        ],
    ]
    return buttons
