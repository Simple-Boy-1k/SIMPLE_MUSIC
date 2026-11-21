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

import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from SIMPLE_MUSIC import LOGGER, app, userbot
from SIMPLE_MUSIC.core.call import SIMPLE
from SIMPLE_MUSIC.core.userbot import assistants
from SIMPLE_MUSIC.misc import sudo
from SIMPLE_MUSIC.plugins import ALL_MODULES
from SIMPLE_MUSIC.utils.database import get_banned_users, get_gbanned
from SIMPLE_MUSIC.utils.vc_alert import attach_vc_join_notifier

COMMANDS = [
    BotCommand("start", "❖ sᴛᴀʀᴛ ʙᴏᴛ • ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
    BotCommand("help", "❖ ʜᴇʟᴘ ᴍᴇɴᴜ • ɢᴇᴛ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ"),
    BotCommand("ping", "❖ ᴘɪɴɢ ʙᴏᴛ • ᴄʜᴇᴄᴋ ᴘɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs"),
]


async def setup_bot_commands():
    try:
        await app.set_bot_commands(COMMANDS)
        LOGGER("SIMPLE_MUSIC").info("Bot commands set successfully!")
    except Exception as e:
        LOGGER("SIMPLE_MUSIC").error(f"Failed to set bot commands: {str(e)}")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "𝐒𝐭𝐫𝐢𝐧𝐠 𝐒𝐞𝐬𝐬𝐢𝐨𝐧 𝐍𝐨𝐭 𝐅𝐢𝐥𝐥𝐞𝐝, 𝐏𝐥𝐞𝐚𝐬𝐞 𝐅𝐢𝐥𝐥 𝐀 𝐏𝐲𝐫𝐨𝐠𝐫𝐚𝐦 𝐒𝐞𝐬𝐬𝐢𝐨𝐧"
        )
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)

    except:
        pass

    await app.start()

    await setup_bot_commands()

    for all_module in ALL_MODULES:
        importlib.import_module("SIMPLE_MUSIC.plugins" + all_module)

    LOGGER("SIMPLE_MUSIC.plugins").info(
        "𝐒𝐢𝐦𝐩𝐥𝐞 𝐁𝐨𝐲 𝐈𝐬 𝐁𝐫𝐚𝐧𝐝🥳..."
    )

    await userbot.start()
    for assistant_num, client_attr in [
        (1, userbot.one),
        (2, userbot.two),
        (3, userbot.three),
        (4, userbot.four),
        (5, userbot.five),
    ]:
        if assistant_num in assistants and client_attr is not None:
            attach_vc_join_notifier(assistant_client=client_attr, main_bot=app)

    await SIMPLE.start()

    try:
        await SIMPLE.stream_call(
            "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
        )

    except NoActiveGroupCall:
        LOGGER("SIMPLE_MUSIC").error(
            "𝗣𝗹𝗭 𝗦𝗧𝗔𝗥𝗧 𝗬𝗢𝗨𝗥 𝗟𝗢𝗚 𝗚𝗥𝗢𝗨𝗣 𝗩𝗢𝗜𝗖𝗘𝗖𝗛𝗔𝗧\\𝗖𝗛𝗔𝗡𝗡𝗘𝗟\n\n𝗦𝗜𝗠𝗣𝗟𝗘 𝗕𝗢𝗧 𝗦𝗧𝗢𝗣........"
        )
        exit()

    except:
        pass

    await SIMPLE.decorators()

    LOGGER("SIMPLE_MUSIC").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠𝗠𝗔𝗗𝗘 𝗕𝗬 𝗦𝗜𝗠𝗣𝗟𝗘 𝗕𝗢𝗬\n╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()

    await app.stop()
    await userbot.stop()

    LOGGER("SIMPLE_MUSIC").info(
        "𝗦𝗧𝗢𝗣 𝗦𝗜𝗠𝗣𝗟𝗘 𝗠𝗨𝗦𝗜𝗖🎻 𝗕𝗢𝗧.."
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
