import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch
import config
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.misc import _boot_
from SIMPLE_MUSIC.plugins.sudo.sudoers import sudoers_list
from SIMPLE_MUSIC.utils import bot_sys_stats
from SIMPLE_MUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from SIMPLE_MUSIC.utils.decorators.language import LanguageStart
from SIMPLE_MUSIC.utils.formatters import get_readable_time
from SIMPLE_MUSIC.utils.inline import help_pannel_page1, private_panel, start_panel
from strings import get_string

# ✅ Purana tareeqa: Wapas START_IMG_URL import kar diya
from config import BANNED_USERS, START_IMG_URL

async def send_logs_bg(message, text_type="started"):
    if await is_on_off(2):
        try:
            text = f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>๏ ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>๏ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}"
            if text_type == "sudolist":
                text = f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>."
            elif text_type == "info":
                text = f"❖ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>."
            await app.send_message(chat_id=config.LOGGER_ID, text=text)
        except:
            pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
async def start_pm(client, message: Message):
    asyncio.create_task(add_served_user(message.from_user.id))
    _ = get_string("en")

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel_page1(_)
            await client.send_photo(
                chat_id=message.chat.id,
                photo=START_IMG_URL,
                caption=_['help_1'].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            asyncio.create_task(send_logs_bg(message, "sudolist"))
            
        elif name.startswith("inf"):
            query = name.replace("info_", "", 1)
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(title, duration, views, published, channellink, channel, app.mention)
            key = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=_["S_B_8"], url=link), InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT)],
            ])
            await client.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            asyncio.create_task(send_logs_bg(message, "info"))
    else:
        out = private_panel(_)
        await client.send_photo(
            chat_id=message.chat.id,
            photo=START_IMG_URL,
            caption=_["start_2"].format(message.from_user.mention, app.mention, "Mina 0.5s", "0.2 GB", "1.2%", "14%", "⚡ Fast", "🔥 Active"),
            reply_markup=InlineKeyboardMarkup(out),
        )
        asyncio.create_task(send_logs_bg(message, "started"))


@app.on_callback_query(filters.regex("home") & ~BANNED_USERS)
@LanguageStart
async def home_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    out = private_panel(_)
    await CallbackQuery.edit_message_text(
        text=_["start_2"].format(CallbackQuery.from_user.mention, app.mention, "Mina 0.5s", "0.2 GB", "1.2%", "14%", "⚡ Fast", "🔥 Active"),
        reply_markup=InlineKeyboardMarkup(out),
    )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await client.send_photo(
        chat_id=message.chat.id,
        photo=START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return asyncio.create_task(add_served_chat(message.chat.id))


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=START_IMG_URL,
                    caption=_["start_3"].format(message.from_user.mention, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                asyncio.create_task(add_served_chat(message.chat.id))
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
