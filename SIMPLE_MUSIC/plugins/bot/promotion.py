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
from SIMPLE_MUSIC.utils.inline.start import private_panel

LOGGER = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

# ======================================================
# CODE MEIN GROUP LINK YAHAN SET KARO (Extra Button)
# ======================================================
EXTRA_GROUP_LINK = "https://t.me/+CBnAUbPjGdlmYzBk"
EXTRA_GROUP_TEXT = "🔥 Join Group 🔥"
# ======================================================

# Ek session mein ek hi user ko baar-baar PM na jaye isliye track set
SENT_PROMO_USERS: set[int] = set()
ADMIN_GROUPS: set[int] = set()


def strip_html_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return html.unescape(cleaned)


def get_bot_username() -> str:
    username = getattr(app, "username", None) or getattr(config, "BOT_USERNAME", "")
    return str(username).lstrip("@")


def find_panel_url_by_text(_, target_text: str) -> str | None:
    """private_panel(_) ke buttons mein se exact text match karke uska url variable uthata hai."""
    if not target_text:
        return None
    try:
        panel = private_panel(_)
        for row in panel:
            for button in row:
                btn_text = getattr(button, "text", None)
                btn_url = getattr(button, "url", None)
                if btn_text == target_text and btn_url:
                    return btn_url
    except Exception:
        LOGGER.exception("Failed to read URL from private_panel")
    return None


def make_promotion_keyboard(_):
    """Auto PM ke liye 3 buttons + neeche code mein set kiya hua extra group button."""

    bot_username = get_bot_username()

    btn_network = _["S_B_2"] if "S_B_2" in _ else "My Network"
    btn_home = _["S_B_6"] if "S_B_6" in _ else "My Home"
    btn_add_group = _["S_B_3"] if "S_B_3" in _ else "✙ Add Me In Group ✙"

    add_group_url = (
        f"https://t.me/{bot_username}?startgroup=true"
        if bot_username
        else getattr(config, "SUPPORT_GROUP", "https://t.me/telegram")
    )

    # My Network -> jo variable mein group link set hai wahi
    network_url = (
        find_panel_url_by_text(_, btn_network)
        or getattr(config, "SUPPORT_GROUP", None)
        or getattr(config, "NETWORK_URL", None)
        or getattr(config, "GROUP_LINK", None)
        or "https://t.me/telegram"
    )

    # My Home -> jo variable mein channel/home link set hai wahi
    home_url = (
        find_panel_url_by_text(_, btn_home)
        or getattr(config, "SUPPORT_CHANNEL", None)
        or getattr(config, "HOME_URL", None)
        or getattr(config, "CHANNEL_LINK", None)
        or "https://t.me/telegram"
    )

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

    # Neeche extra group button jo code ke EXTRA_GROUP_LINK se aayega
    if EXTRA_GROUP_LINK and EXTRA_GROUP_LINK.startswith(("http://", "https://", "tg://")):
        keyboard.append(
            [
                {
                    "text": EXTRA_GROUP_TEXT,
                    "url": EXTRA_GROUP_LINK,
                    "style": "danger",
                }
            ]
        )

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


async def send_promotion_to_user(session, user: dict, source: str = "promo"):
    if not user or user.get("is_bot"):
        return

    user_id = user.get("id")
    if not user_id:
        LOGGER.warning("Update has no user id (%s)", source)
        return

    if user_id in SENT_PROMO_USERS:
        return

    try:
        _ = get_string("en")

        raw_first_name = user.get("first_name") or "Friend"
        first_name = html.escape(str(raw_first_name))

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
            "chat_id": user_id,
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
                    "chat_id": user_id,
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
            elif "bot can't initiate conversation" in desc or "blocked" in desc.lower():
                LOGGER.info(
                    "Cannot DM user %s (%s): %s",
                    user_id,
                    source,
                    desc,
                )
                return
            else:
                LOGGER.error("Telegram API sendPhoto error: %s", result)

        if result.get("ok"):
            SENT_PROMO_USERS.add(user_id)
            LOGGER.info(
                "Promotion sent to user %s via %s",
                user_id,
                source,
            )

    except Exception:
        LOGGER.exception("Promotion sending failed")


async def handle_join_request(session, update: dict):
    request = update.get("chat_join_request", {})
    user = request.get("from", {})
    await send_promotion_to_user(session, user, source="chat_join_request")


async def handle_chat_member_update(session, update: dict):
    cm = update.get("chat_member", {})
    old_member = cm.get("old_chat_member", {})
    new_member = cm.get("new_chat_member", {})

    old_status = old_member.get("status")
    new_status = new_member.get("status")

    joined_statuses = {"member", "administrator", "creator"}
    left_statuses = {"left", "kicked", "banned", None}

    if old_status in left_statuses and new_status in joined_statuses:
        user = new_member.get("user") or cm.get("from", {})
        await send_promotion_to_user(session, user, source="chat_member_join")


async def handle_my_chat_member_update(update: dict):
    mcm = update.get("my_chat_member", {})
    chat = mcm.get("chat", {})
    new_member = mcm.get("new_chat_member", {})

    chat_id = chat.get("id")
    new_status = new_member.get("status")

    if chat_id and new_status in {"administrator", "creator"}:
        ADMIN_GROUPS.add(chat_id)
        LOGGER.info(
            "Bot promoted to %s in chat %s (%s)",
            new_status,
            chat.get("title"),
            chat_id,
        )
    elif chat_id and new_status in {"left", "kicked", "banned"}:
        ADMIN_GROUPS.discard(chat_id)


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
                        [
                            "chat_join_request",
                            "chat_member",
                            "my_chat_member",
                        ]
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
                        await handle_join_request(session, update)
                    elif "chat_member" in update:
                        await handle_chat_member_update(session, update)
                    elif "my_chat_member" in update:
                        await handle_my_chat_member_update(update)

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
