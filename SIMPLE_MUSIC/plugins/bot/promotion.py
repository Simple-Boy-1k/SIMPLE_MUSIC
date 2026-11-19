# -----------------------------------------------
# SIMPLE MUSIC - AUTO PM PROMOTION
# Developed by: Simple Boy
# -----------------------------------------------

import asyncio
import html
import json
import logging
import re

import aiohttp
import config

from strings import get_string
from SIMPLE_MUSIC import app

LOGGER = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def strip_html_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return html.unescape(cleaned)


def get_bot_username() -> str:
    username = getattr(app, "username", None) or getattr(config, "BOT_USERNAME", "")
    return str(username).lstrip("@")


def make_promotion_keyboard(_):
    """Auto PM ke liye 3 buttons (danger color mein):
    - Add Me In Group
    - My Network (Group link)
    - My Home (Channel link)
    """

    bot_username = get_bot_username()

    add_group_url = (
        f"https://t.me/{bot_username}?startgroup=true"
        if bot_username
        else getattr(config, "SUPPORT_GROUP", "https://t.me/telegram")
    )

    # My Network -> Group link
    network_url = (
        getattr(config, "SUPPORT_GROUP", None)
        or getattr(config, "NETWORK_URL", None)
        or (f"https://t.me/{bot_username}" if bot_username else "https://t.me/telegram")
    )

    # My Home -> Channel link
    home_url = (
        getattr(config, "SUPPORT_CHANNEL", None)
        or getattr(config, "HOME_URL", None)
        or (f"https://t.me/{bot_username}" if bot_username else "https://t.me/telegram")
    )

    btn_add_group = _["S_B_3"] if "S_B_3" in _ else "✙ Add Me In Group ✙"
    btn_network = _["S_B_2"] if "S_B_2" in _ else "My Network"
    btn_home = _["S_B_6"] if "S_B_6" in _ else "My Home"

    keyboard = [
        [
            {
                "text": btn_add_group,
                "url": add_group_url,
                "style": "danger",
            }
        ],
        [
            {
                "text": btn_network,
                "url": network_url,
                "style": "danger",
            },
            {
                "text": btn_home,
                "url": home_url,
                "style": "danger",
            },
        ],
    ]

    return {"inline_keyboard": keyboard}


async def api_call(session, method, data, log_error=True):
    url = f"{BOT_API}/{method}"

    async with session.post(
        url,
        json=data,
        timeout=aiohttp.ClientTimeout(total=35)
    ) as response:
        result = await response.json()

        if not result.get("ok") and log_error:
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

        raw_first_name = user.get("first_name") or "Friend"
        first_name = html.escape(str(raw_first_name))
        user_id = user.get("id")

        mention = (
            f'<a href="tg://user?id={user_id}">'
            f'{first_name}</a>'
        )

        bot_mention = str(getattr(app, "mention", "") or "")
        if not bot_mention.startswith("<"):
            bot_mention = html.escape(bot_mention)

        caption = _["start_2"].format(
            mention,
            bot_mention,
            html.escape("Mina 0.5s"),
            html.escape("0.2 GB"),
            html.escape("1.2%"),
            html.escape("14%"),
            html.escape("⚡ Fast"),
            html.escape("🔥 Active"),
        )

        reply_markup = make_promotion_keyboard(_)

        data = {
            "chat_id": user_chat_id,
            "photo": config.START_IMG_URL,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": reply_markup,
        }

        result = await api_call(
            session,
            "sendPhoto",
            data,
            log_error=False,
        )

        if not result.get("ok"):
            desc = str(result.get("description", ""))
            if "can't parse entities" in desc:
                fallback_data = {
                    "chat_id": user_chat_id,
                    "photo": config.START_IMG_URL,
                    "caption": strip_html_tags(caption),
                    "reply_markup": reply_markup,
                }
                result = await api_call(
                    session,
                    "sendPhoto",
                    fallback_data,
                    log_error=True,
                )
            else:
                LOGGER.error("Telegram API sendPhoto error: %s", result)

        if result.get("ok"):
            LOGGER.info(
                "Promotion sent to user %s",
                user_id,
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
