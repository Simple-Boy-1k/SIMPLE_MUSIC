# -----------------------------------------------
# SIMPLE MUSIC - AUTO PM PROMOTION
# Developed by: Simple Boy
# -----------------------------------------------

import asyncio
import html
import logging
import re

import aiohttp
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated

import config
from strings import get_string
from SIMPLE_MUSIC import app
from SIMPLE_MUSIC.utils.inline.start import private_panel

LOGGER = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

# ======================================================
# BUTTONS KE NEECHE ALAG MESSAGE MEIN AANE WALA LINK (DP Preview ON)
# ======================================================
EXTRA_GROUP_LINK = "https://t.me/+CBnAUbPjGdlmYzBk"
# ======================================================

SENT_PROMO_USERS: set[int] = set()
ADMIN_GROUPS: set[int] = set()


def strip_html_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return html.unescape(cleaned)


def get_bot_username() -> str:
    username = getattr(app, "username", None) or getattr(config, "BOT_USERNAME", "")
    return str(username).lstrip("@")


def get_promotion_photo() -> str | None:
    """config se DP / start image URL uthata hai."""
    candidates = [
        getattr(config, "START_IMG_URL", None),
        getattr(config, "START_PIC", None),
        getattr(config, "PING_IMG_URL", None),
        getattr(config, "STATS_IMG_URL", None),
    ]
    for img in candidates:
        if img and str(img).strip():
            return str(img).strip()
    return None


def find_panel_url_by_text(_, target_text: str) -> str | None:
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
    """Auto PM ke liye sirf 3 buttons (danger color mein)."""

    bot_username = get_bot_username()

    btn_network = _["S_B_2"] if "S_B_2" in _ else "My Network"
    btn_home = _["S_B_6"] if "S_B_6" in _ else "My Home"
    btn_add_group = _["S_B_3"] if "S_B_3" in _ else "✙ Add Me In Group ✙"

    add_group_url = (
        f"https://t.me/{bot_username}?startgroup=true"
        if bot_username
        else getattr(config, "SUPPORT_GROUP", "https://t.me/telegram")
    )

    network_url = (
        find_panel_url_by_text(_, btn_network)
        or getattr(config, "SUPPORT_GROUP", None)
        or getattr(config, "NETWORK_URL", None)
        or getattr(config, "GROUP_LINK", None)
        or "https://t.me/telegram"
    )

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

    return {"inline_keyboard": keyboard}


def build_caption(_, user_id: int, first_name_raw: str | None) -> str:
    first_name = html.escape(str(first_name_raw or "Friend"))
    mention = f'<a href="tg://user?id={user_id}">{first_name}</a>'

    bot_mention = str(getattr(app, "mention", "") or "")
    if not bot_mention.startswith("<"):
        bot_mention = html.escape(bot_mention)

    if "start_2" in _:
        return _["start_2"].format(
            mention,
            bot_mention,
            html.escape("Mina 0.5s"),
            html.escape("0.2 GB"),
            html.escape("1.2%"),
            html.escape("14%"),
            html.escape("⚡ Fast"),
            html.escape("🔥 Active"),
        )

    return f"<b>Hello {mention}! Welcome to {bot_mention}</b>"


async def bot_api_post(method: str, payload: dict, log_error: bool = True) -> dict:
    url = f"{BOT_API}/{method}"
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if not data.get("ok") and log_error:
                LOGGER.error("Telegram Bot API %s error: %s", method, data)
            return data


async def send_separate_link_message(user_id: int):
    """Buttons wale main message ke baad alag se link + uski DP preview bhejta hai."""
    if not EXTRA_GROUP_LINK or not EXTRA_GROUP_LINK.strip():
        return

    link_text = EXTRA_GROUP_LINK.strip()
    payload = {
        "chat_id": user_id,
        "text": link_text,
        "link_preview_options": {
            "is_disabled": False,
            "url": link_text,
            "prefer_large_media": True,
        },
    }
    await bot_api_post("sendMessage", payload, log_error=True)


async def send_promotion_pm(
    user_id: int,
    first_name: str | None,
    is_bot: bool = False,
    source: str = "promo",
):
    if not user_id or is_bot:
        return

    if user_id in SENT_PROMO_USERS:
        return

    try:
        _ = get_string("en")
        caption = build_caption(_, user_id, first_name)
        reply_markup = make_promotion_keyboard(_)
        photo = get_promotion_photo()

        if photo:
            payload = {
                "chat_id": user_id,
                "photo": photo,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup,
            }
            result = await bot_api_post("sendPhoto", payload, log_error=False)

            if not result.get("ok"):
                desc = str(result.get("description", ""))
                if "can't parse entities" in desc:
                    fallback_payload = {
                        "chat_id": user_id,
                        "photo": photo,
                        "caption": strip_html_tags(caption),
                        "reply_markup": reply_markup,
                    }
                    result = await bot_api_post("sendPhoto", fallback_payload, log_error=False)

                if not result.get("ok"):
                    new_desc = str(result.get("description", ""))
                    if (
                        "bot can't initiate conversation" in new_desc.lower()
                        or "blocked" in new_desc.lower()
                    ):
                        LOGGER.warning(
                            "User %s hasn't started bot or blocked PM (%s)",
                            user_id,
                            source,
                        )
                        return

                    msg_payload = {
                        "chat_id": user_id,
                        "text": strip_html_tags(caption),
                        "link_preview_options": {"is_disabled": True},
                        "reply_markup": reply_markup,
                    }
                    result = await bot_api_post("sendMessage", msg_payload, log_error=True)
        else:
            msg_payload = {
                "chat_id": user_id,
                "text": caption,
                "parse_mode": "HTML",
                "link_preview_options": {"is_disabled": True},
                "reply_markup": reply_markup,
            }
            result = await bot_api_post("sendMessage", msg_payload, log_error=True)

        if result.get("ok"):
            SENT_PROMO_USERS.add(user_id)
            LOGGER.info("Promotion PM sent to user %s via %s", user_id, source)
            await asyncio.sleep(0.3)
            await send_separate_link_message(user_id)

    except Exception:
        LOGGER.exception("Failed to send promotion PM to %s", user_id)


@app.on_chat_join_request()
async def on_join_request(_, join_request: ChatJoinRequest):
    user = join_request.from_user
    if not user:
        return
    LOGGER.info(
        "Join request received from user %s in chat %s",
        user.id,
        join_request.chat.id if join_request.chat else None,
    )
    await send_promotion_pm(
        user_id=user.id,
        first_name=user.first_name,
        is_bot=bool(user.is_bot),
        source="chat_join_request",
    )


@app.on_chat_member_updated()
async def on_chat_member_update(_, update: ChatMemberUpdated):
    if update.new_chat_member and update.new_chat_member.user and update.new_chat_member.user.is_self:
        chat_id = update.chat.id if update.chat else None
        status = getattr(
            update.new_chat_member.status,
            "value",
            str(update.new_chat_member.status),
        ).lower()
        if chat_id and status in {
            "administrator",
            "creator",
            "chatmemberstatus.administrator",
            "chatmemberstatus.creator",
        }:
            ADMIN_GROUPS.add(chat_id)
            LOGGER.info("Bot promoted to %s in chat %s", status, chat_id)
        elif chat_id and status in {
            "left",
            "banned",
            "kicked",
            "chatmemberstatus.left",
            "chatmemberstatus.banned",
        }:
            ADMIN_GROUPS.discard(chat_id)
        return

    old_m = update.old_chat_member
    new_m = update.new_chat_member
    if not new_m or not new_m.user:
        return

    old_status = (
        getattr(old_m.status, "value", str(old_m.status)).lower()
        if old_m and old_m.status
        else "left"
    )
    new_status = (
        getattr(new_m.status, "value", str(new_m.status)).lower()
        if new_m.status
        else ""
    )

    joined_set = {
        "member",
        "administrator",
        "creator",
        "chatmemberstatus.member",
        "chatmemberstatus.administrator",
        "chatmemberstatus.creator",
    }
    left_set = {
        "left",
        "banned",
        "kicked",
        "restricted",
        "chatmemberstatus.left",
        "chatmemberstatus.banned",
        "chatmemberstatus.kicked",
        "",
    }

    if old_status in left_set and new_status in joined_set:
        user = new_m.user
        LOGGER.info(
            "Member joined: user %s in chat %s",
            user.id,
            update.chat.id if update.chat else None,
        )
        await send_promotion_pm(
            user_id=user.id,
            first_name=user.first_name,
            is_bot=bool(user.is_bot),
            source="chat_member_join",
        )
