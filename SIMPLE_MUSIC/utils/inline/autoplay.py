import asyncio
from pyrogram import filters
from pyrogram.types import CallbackQuery
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.utils.inline import stream_markup

# Chat-wise autoplay status store karne ke liye dictionary
autoplay_status = {}

@app.on_callback_query(filters.regex("AutoplayToggle"))
async def toggle_autoplay_callback(_, query: CallbackQuery):
    try:
        data = query.data.split()
        chat_id = int(data[1])
    except Exception:
        chat_id = query.message.chat.id

    # Current state check karein (Default True/ON rahega)
    current_state = autoplay_status.get(chat_id, True)
    new_state = not current_state
    autoplay_status[chat_id] = new_state

    status_text = "ON" if new_state else "OFF"
    await query.answer(f"Autoplay is now {status_text}!", show_alert=False)

    try:
        markup = stream_markup(_, chat_id)
        await query.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@app.on_callback_query(filters.regex("AutoplaySkip"))
async def autoplay_skip_callback(_, query: CallbackQuery):
    try:
        data = query.data.split()
        chat_id = int(data[1])
    except Exception:
        chat_id = query.message.chat.id

    await query.answer("Skipping to next autoplay track...", show_alert=False)
    
    # Yahan aap skip function ya next track play karne ka logic call kar sakte hain
    # Jaise baki skip buttons kaam karte hain
