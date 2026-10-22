# -----------------------------------------------
# 🔸 SIMPLE MUSIC Project
# 🔹 Developed & Maintained by: Simple Boy (https://github.com/Simple-Boy-1k)
# 📅 Copyright © 2026 – All Rights Reserved
# -----------------------------------------------
from pyrogram import filters
from pyrogram.types import Message
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.utils.database import stop_db, stop_all_db
from config import BANNED_USERS

@app.on_message(
    filters.command(["delfilter", "stopfilter"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]) 
    & filters.group 
    & ~BANNED_USERS
)
async def delete_custom_filter(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Kripya filter ka naam likhein!**\n"
            "Udaharan: `/delfilter hello` ya `/stopfilter hi`"
        )
    
    chat_id = message.chat.id
    filter_name = message.command[1]
    
    # Database se filter delete karne ka function call
    deleted = await stop_db(chat_id, filter_name)
    
    if deleted:
        await message.reply_text(f"✅ Filter **`{filter_name}`** ko safalpurvak hata diya gaya hai!")
    else:
        await message.reply_text(f"❌ Is naam se koi filter nahi mila: **`{filter_name}`**")


@app.on_message(
    filters.command(["stopallfilters", "delfiltersall"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]) 
    & filters.group 
    & ~BANNED_USERS
)
async def delete_all_custom_filters(client, message: Message):
    chat_id = message.chat.id
    await stop_all_db(chat_id)
    await message.reply_text("🗑️ Is chat ke saare custom filters hata diye gaye hain!")
