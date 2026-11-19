
# -----------------------------------------------
# SIMPLE MUSIC - AUTO PM PROMOTION
# Developed by: Simple Boy
# -----------------------------------------------

import asyncio
import html
import json
import logging

import aiohttp
import config

from strings import get_string
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.utils.inline.start import private_panel

LOGGER = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def make_keyboard(_):
    """Reuse existing /start inline buttons."""

    panel = private_panel(_)
    keyboard = []

    for row in panel:
        new_row = []

        for button in row:
            item = {"text": button.text}

            # Owner button: convert user_id button to profile URL
            user_id = getattr(button, "user_id", None)

            if user_id:
                username = getattr(config, "OWNER_USERNAME", "")
                if username:
                    item["url"] = f"https://t.me/{username.lstrip('@')}"
                else:
                    item["url"] = f"tg://user?id={user_id}"

            elif getattr(button, "url", None):
                item["url"] = button.url

            elif getattr(button, "callback_data", None):
                data = button.callback_data
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                item["callback_data"] = str(data)

            else:
                continue

            new_row.append(item)

        if new_row:
            keyboard.append(new_row)

    return {"inline_keyboard": keyboard}


async def api_call(session, method, data):
    url = f"{BOT_API}/{method}"

    async with session.post(
        url,
        json=data,
        timeout=aiohttp.ClientTimeout(total=35)
    ) as response:
        result = await response.json()

        if not result.get("ok"):
            LOGGER.error(
                "Telegram API %s error: %s",
                method,
                result
            )

        return result


async def send_promotion(session, update):
    request = update.get("chat_join_request", {})

    user_chat_id = request.get("user_chat_id")
    user = request.get("from", {})

    if not user_chat_id:
        LOGGER.warning("Join request has no user_chat_id")
        return

    try:
        _ = get_string("en")

        first_name = html.escape(user.get("first_name", "Friend"))
        user_id = user.get("id")

        mention = (
            f'<a href="tg://user?id={user_id}">'
            f'{first_name}</a>'
        )

        caption = _["start_2"].format(
            mention,
            app.mention,
            "Mina 0.5s",
            "0.2 GB",
            "1.2%",
            "14%",
            "⚡ Fast",
            "🔥 Active"
        )

        data = {
            "chat_id": user_chat_id,
            "photo": config.START_IMG_URL,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": make_keyboard(_)
        }

        result = await api_call(
            session,
            "sendPhoto",
            data
        )

        if result.get("ok"):
            LOGGER.info(
                "Promotion sent to user %s",
                user_id
            )

    except Exception:
        LOGGER.exception("Promotion sending failed")


async def promotion_listener():
    offset = None

    timeout = aiohttp.ClientTimeout(total=40)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        # Check whether webhook is active
        try:
            info = await api_call(
                session,
                "getWebhookInfo",
                {}
            )

            if info.get("ok") and info["result"].get("url"):
                LOGGER.error(
                    "Promotion listener stopped: "
                    "Telegram webhook is active. "
                    "getUpdates cannot run with a webhook."
                )
                return

        except Exception:
            LOGGER.exception("Webhook check failed")
            return

        LOGGER.info("Auto Promotion Listener Started")

        while True:
            try:
                params = {
                    "timeout": 25,
                    "allowed_updates": json.dumps(
                        ["chat_join_request"]
                    )
                }

                if offset is not None:
                    params["offset"] = offset

                async with session.get(
                    f"{BOT_API}/getUpdates",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=35)
                ) as response:

                    result = await response.json()

                if not result.get("ok"):
                    LOGGER.error(
                        "getUpdates error: %s",
                        result
                    )
                    await asyncio.sleep(5)
                    continue

                for update in result.get("result", []):
                    offset = update["update_id"] + 1

                    if "chat_join_request" in update:
                        await send_promotion(
                            session,
                            update
                        )

            except asyncio.CancelledError:
                raise

            except Exception:
                LOGGER.exception(
                    "Promotion listener error"
                )
                await asyncio.sleep(5)


# Start listener when plugin loads
asyncio.get_running_loop().create_task(
    promotion_listener()
)
