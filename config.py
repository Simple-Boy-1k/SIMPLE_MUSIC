# ------------------------------------------
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
# ------------------------------------------

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ʀ ᴇ ǫ ᴜ ɪ ʀ ᴇ ᴅ   ᴄ ʀ ᴇ ᴅ ᴇ ɴ ᴛ ɪ ᴀ ʟ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ʙ ᴏ ᴛ   ᴀ ɴ ᴅ   ᴏ ᴡ ɴ ᴇ ʀ   ɪ ɴ ғ ᴏ ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OWNER_USERNAME = getenv("OWNER_USERNAME", "Simple_Boy_1k")
BOT_USERNAME = getenv("BOT_USERNAME", "Senorita_Music11_Bot")
BOT_NAME = getenv("BOT_NAME", "SENORITA")
ASSUSERNAME = getenv("ASSUSERNAME", "Simple_Boy_1k")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴅ ᴀ ᴛ ᴀ ʙ ᴀ s ᴇ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONGO_DB_URI = getenv("MONGO_DB_URI", None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴀ ᴘ ɪ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YTPROXY_URL = getenv("YTPROXY_URL", "https://tgapi.xbitcode.com")
YT_API_KEY = getenv("YT_API_KEY", "") # youtube song api key, generate free key or buy paid plan from http://music.xbitcode.com
API_URL = getenv("API_URL", "https://api.nexgenbots.xyz") #youtube song url
VIDEO_API_URL = getenv("VIDEO_API_URL", 'https://api.video.nexgenbots.xyz')
API_KEY = getenv("API_KEY", "") # youtube song api key, generate free key or buy paid plan from https://console.nexgenbots.xyz

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ʟ ɪ ᴍ ɪ ᴛ s   ᴀ ɴ ᴅ   ɪ ᴅ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ DURATION LIMIT MAXED OUT FOR UNLIMITED PLAYBACK
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 999999))
LOGGER_ID = int(getenv("LOGGER_ID", -1003455128274))
OWNER_ID = int(getenv("OWNER_ID", 8730025963))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ʜ ᴇ ʀ ᴏ ᴋ ᴜ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
DEEP_API = getenv("DEEP_API")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ɢ ɪ ᴛ ʜ ᴜ ʙ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Simple-Boy-1k/SIMPLE_MUSIC")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ s ᴜ ᴘ ᴘ ᴏ ʀ ᴛ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/music_Bot_Adda")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+wcALPiJtMCQ0NWFh")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴀ s s ɪ s ᴛ ᴀ ɴ ᴛ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴅ ᴏ ᴡ ɴ ʟ ᴏ ᴀ ᴅ   ʟ ɪ ᴍ ɪ ᴛ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ s ᴘ ᴏ ᴛ ɪ ғ ʏ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴘ ʟ ᴀ ʏ ʟ ɪ s ᴛ   s ᴇ ᴛ ᴛ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 500))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴛ ᴇ ʟ ᴇ ɢ ʀ ᴀ ᴍ   ғ ɪ ʟ ᴇ   ʟ ɪ ᴍ ɪ ᴛ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ s ᴇ s s ɪ ᴏ ɴ   s ᴛ ʀ ɪ ɴ ɢ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)
STRING6 = getenv("STRING_SESSION6", None)
STRING7 = getenv("STRING_SESSION7", None)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ᴍ ɪ s ᴄ ᴇ ʟ ʟ ᴀ ɴ ᴇ ᴏ ᴜ s  s ᴇ ᴛ ᴛ ɪ ɴ ɢ s
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUTTON_COLOUR = getenv("BUTTON_COLOUR", "True").lower() == "true"
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
DEBUG_IGNORE_LOG = True


# ━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ɪ ᴍ ᴀ ɢ ᴇ   ᴜ ʀ ʟ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━
START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/z1h6ow.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/j40lbb.png")
HELP_IMG_URL = getenv("HELP_IMG_URL", "https://files.catbox.moe/b7qhd8.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/cc6f5z.jpg"
STATS_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/z1h6ow.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/z1h6ow.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/37omve.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/z1h6ow.jpg"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❖ ʜ ᴇ ʟ ᴘ ᴇ ʀ   ғ ᴜ ɴ ᴄ ᴛ ɪ ᴏ ɴ s ❖
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def time_to_seconds(time: str) -> int:
    """Convert time string (MM:SS) to total seconds."""
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is invalid. It must start with https://")

if SUPPORT_CHAT and not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is invalid. It must start with https://")
