from typing import Union
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from SIMPLE_MUSIC import app

# Chat-wise autoplay status store karne ke liye dictionary
autoplay_status = {}

@app.on_callback_query(filters.regex("AutoplayToggle"))
async def toggle_autoplay_callback(_, query: CallbackQuery):
    try:
        data = query.data.split()
        chat_id = int(data[1])
    except Exception:
        chat_id = query.message.chat.id

    current_state = autoplay_status.get(chat_id, True)
    new_state = not current_state
    autoplay_status[chat_id] = new_state

    # Bina kisi pop-up alert ke seedha toggle karne ke liye
    await query.answer()

    try:
        markup = aq_markup(_, chat_id)
        await query.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text="ǫᴜᴇᴜᴇ",
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text="ᴄʟᴏꜱᴇ",
                callback_data="close",
            ),
        ]
    ]
    dur_list = [
        [
            InlineKeyboardButton(
                text=f"{played} / {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text="ǫᴜᴇᴜᴇ",
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text="ᴄʟᴏꜱᴇ",
                callback_data="close",
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur_list)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="ʙᴀᴄᴋ",
                    callback_data=f"queue_back_timer {CPLAY}",
                ),
                InlineKeyboardButton(
                    text="ᴄʟᴏꜱᴇ",
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    is_autoplay = autoplay_status.get(chat_id, True)
    autoplay_text = "ᴀᴜᴛᴏᴘʟᴀʏ : ᴇɴᴀʙʟᴇᴅ" if is_autoplay else "ᴀᴜᴛᴏᴘʟᴀʏ : ᴅɪꜱᴀʙʟᴇᴅ"

    buttons = [
        [
            InlineKeyboardButton(
                text="ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=autoplay_text, callback_data=f"AutoplayToggle {chat_id}"),
        ],
        [
            InlineKeyboardButton(text="ᴄʟᴏꜱᴇ", callback_data="close"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)
