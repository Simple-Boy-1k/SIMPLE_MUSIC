
# -----------------------------------------------
# SIMPLE MUSIC - AUTO JOIN REQUEST PROMOTION
# -----------------------------------------------

import asyncio
from logging import getLogger

from pyrogram.handlers import ChatJoinRequestHandler

import config
from SIMPLE_MUSIC import app
from config import START_IMG_URL
from SIMPLE_MUSIC.utils.inline import private_panel
from strings import get_string

LOGGER = getLogger(__name__)


async def auto_promotion(client, request):
    try:
        # Temporary private chat ID from Join Request
        user_chat_id = request.user_chat_id

        # Existing bot language strings
        _ = get_string("en")

        # Existing /start buttons and their styles
        keyboard = private_panel(_)

        # Same caption as existing /start message
        caption = _["start_2"].format(
            request.from_user.mention,
            app.mention,
            "Mina 0.5s",
            "0.2 GB",
            "1.2%",
            "14%",
            "⚡ Fast",
            "🔥 Active"
        )

        # Same DP and design as existing /start
        await client.send_photo(
            chat_id=user_chat_id,
            photo=START_IMG_URL,
            caption=caption,
            reply_markup=keyboard,
        )

        LOGGER.info(
            "Promotion sent to join request user: %s",
            request.from_user.id
        )

    except Exception:
        LOGGER.exception("Auto promotion failed")


app.add_handler(
    ChatJoinRequestHandler(auto_promotion)
)
