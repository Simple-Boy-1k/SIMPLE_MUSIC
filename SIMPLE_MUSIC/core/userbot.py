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
import sys
from pyrogram import Client
import config
from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="SIMPLEAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=False,
        )
        self.two = Client(
            name="SIMPLEAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=False,
        )
        self.three = Client(
            name="SIMPLEAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=False,
        )
        self.four = Client(
            name="SIMPLEAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=False,
        )
        self.five = Client(
            name="SIMPLEAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=False,
        )

    async def _join_default_chats(self, client: Client):
        for chat_username in ("The_LuckyX", "music_Bot_Adda"):
            try:
                await client.join_chat(chat_username)
            except Exception:
                pass

    async def _init_assistant(self, client: Client, num: int, label: str):
        await client.start()
        await self._join_default_chats(client)
        assistants.append(num)
        try:
            await client.send_message(config.LOGGER_ID, "Assistant Started")
        except Exception:
            LOGGER(__name__).error(
                f"Assistant Account {num} has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
            )
            sys.exit(1)
        client.id = client.me.id
        client.name = client.me.mention
        client.username = client.me.username
        assistantids.append(client.id)
        LOGGER(__name__).info(f"Assistant {label} Started as {client.name}")

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")
        if config.STRING1:
            await self._init_assistant(self.one, 1, "One")
        if config.STRING2:
            await self._init_assistant(self.two, 2, "Two")
        if config.STRING3:
            await self._init_assistant(self.three, 3, "Three")
        if config.STRING4:
            await self._init_assistant(self.four, 4, "Four")
        if config.STRING5:
            await self._init_assistant(self.five, 5, "Five")

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        for string_val, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if string_val:
                try:
                    await client.stop()
                except Exception:
                    pass
