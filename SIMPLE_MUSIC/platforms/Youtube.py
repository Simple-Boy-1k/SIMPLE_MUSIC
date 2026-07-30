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
import os
import re
from typing import Union

import aiohttp
import aiofiles
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

from SIMPLE_MUSIC import LOGGER
from SIMPLE_MUSIC.utils.formatters import time_to_seconds

from config import API_URL, VIDEO_API_URL, API_KEY, YT_API_KEY, YTPROXY_URL

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
CLIENT_SESSION = None

async def get_session():
    global CLIENT_SESSION
    if CLIENT_SESSION is None or CLIENT_SESSION.closed:
        CLIENT_SESSION = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0))
    return CLIENT_SESSION

async def _download_stream(url, path, headers=None):
    try:
        session = await get_session()
        # total=None means full download ka koi time limit nahi (Error nahi aayega)
        # sock_read=20 means agar connection 20s tak atak jaye tab retry karega
        timeout = aiohttp.ClientTimeout(total=None, sock_read=20) 
        
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                async with aiofiles.open(path, mode='wb') as f:
                    # 2MB Chunk Size - RAM kabhi crash nahi hoga
                    async for chunk in response.content.iter_chunked(2 * 1024 * 1024):
                        await f.write(chunk)
                if os.path.exists(path) and os.path.getsize(path) > 1024:
                    return path
    except:
        pass
    if os.path.exists(path):
        try: os.remove(path)
        except: pass
    return None

async def engine_shrutibots(vid_id: str, is_video: bool, path: str) -> str:
    try:
        session = await get_session()
        v_type = "video" if is_video else "audio"
        async with session.get(f"{API_URL}/download", params={"url": vid_id, "type": v_type}, timeout=7) as resp:
            if resp.status != 200: return None
            token = (await resp.json()).get("download_token")
            if not token: return None
        return await _download_stream(f"{API_URL}/stream/{vid_id}?type={v_type}&token={token}", path)
    except: return None

async def engine_xbit(vid_id: str, is_video: bool, path: str) -> str:
    if not YTPROXY_URL or not YT_API_KEY: return None
    try:
        session = await get_session()
        headers = {"x-api-key": YT_API_KEY}
        async with session.get(f"{YTPROXY_URL}/info/{vid_id}", headers=headers, timeout=7) as resp:
            if resp.status != 200: return None
            data = await resp.json()
        if data.get('status') == 'success':
            url = data['video_url'] if is_video else data['audio_url']
            return await _download_stream(url, path, headers)
    except: return None

async def engine_nexgen(vid_id: str, is_video: bool, path: str) -> str:
    if not API_KEY: return None
    try:
        url = f"{VIDEO_API_URL}/video/{vid_id}?api={API_KEY}" if is_video else f"{API_URL}/song/{vid_id}?api={API_KEY}"
        session = await get_session()
        async with session.get(url, timeout=7) as resp:
            if resp.status != 200: return None
            data = await resp.json()
            if data.get("status", "").lower() == "done" and data.get("link"):
                return await _download_stream(data.get("link"), path)
    except: return None

async def _core_download(link: str, is_video: bool) -> str:
    vid_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link.split("/")[-1].split("?")[0]
    ext = "mp4" if is_video else "mp3"
    final_path = os.path.join(DOWNLOAD_DIR, f"{vid_id}.{ext}")

    if os.path.exists(final_path) and os.path.getsize(final_path) > 1024:
        return final_path

    tasks = [
        asyncio.create_task(engine_shrutibots(vid_id, is_video, f"{final_path}_shruti")),
        asyncio.create_task(engine_xbit(vid_id, is_video, f"{final_path}_xbit")),
        asyncio.create_task(engine_nexgen(vid_id, is_video, f"{final_path}_nexgen"))
    ]

    winner = None
    for future in asyncio.as_completed(tasks):
        try:
            res = await future
            if res:
                winner = res
                for t in tasks: t.cancel()
                break
        except: pass

    if winner and os.path.exists(winner):
        try:
            os.rename(winner, final_path)
            return final_path
        except:
            return winner

    loop = asyncio.get_running_loop()
    def fallback_ytdl():
        opts = {
            "format": "bestvideo[height<=480][fps<=30][ext=mp4]+bestaudio[ext=m4a]/best" if is_video else "bestaudio/best",
            "outtmpl": final_path,
            "quiet": True, "nocheckcertificate": True, "no_warnings": True, "ignoreerrors": True,
        }
        if not is_video: opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
        yt_dlp.YoutubeDL(opts).download([link])
        
    await loop.run_in_executor(None, fallback_ytdl)
    
    if os.path.exists(final_path) and os.path.getsize(final_path) > 1024:
        return final_path
    return None

async def download_song(link: str) -> str:
    return await _core_download(link, is_video=False)

async def download_video(link: str) -> str:
    return await _core_download(link, is_video=True)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for msg in messages:
            for ent in (msg.entities or []):
                if ent.type == MessageEntityType.URL: return (msg.text or msg.caption)[ent.offset : ent.offset + ent.length]
            for ent in (msg.caption_entities or []):
                if ent.type == MessageEntityType.TEXT_LINK: return ent.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        return (await self.details(link, videoid))[0]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        return (await self.details(link, videoid))[1]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        return (await self.details(link, videoid))[3]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            res = await download_video(link)
            return (1, res) if res else (0, "Video download failed")
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        try:
            videos = (await Playlist.get(link)).get("videos") or []
            return [data["id"] for data in videos[:limit] if data and data.get("id")]
        except: return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return {"title": result["title"], "link": result["link"], "vidid": result["id"], "duration_min": result["duration"], "thumb": result["thumbnails"][0]["url"].split("?")[0]}, result["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            return [{"format": f["format"], "filesize": f.get("filesize"), "format_id": f["format_id"], "ext": f["ext"], "format_note": f.get("format_note"), "yturl": link} for f in ydl.extract_info(link, download=False)["formats"] if "dash" not in str(f.get("format", "")).lower()], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = (await VideosSearch(link, limit=10).next()).get("result")[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def download(
        self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None, title: Union[bool, str] = None,
    ) -> str:
        if videoid: link = self.base + link
        
        is_video = bool(video)
        vid_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link.split("/")[-1].split("?")[0]

        duration_sec = 0
        is_live = False
        try:
            _, _, duration_sec, _, _ = await self.details(link)
        except:
            is_live = True

        # ⚡ 1 HOUR LIMIT BYPASS (>3600 sec)
        if is_live or duration_sec == 0 or duration_sec > 3600:
            try:
                session = await get_session()
                async with session.get(f"{YTPROXY_URL}/info/{vid_id}", headers={"x-api-key": YT_API_KEY}, timeout=3) as r:
                    if r.status == 200:
                        data = await r.json()
                        stream_url = data.get('video_url') if is_video else data.get('audio_url')
                        if stream_url: return stream_url, False 
            except: pass
            
            loop = asyncio.get_running_loop()
            def extract_direct_url():
                format_str = "bestvideo[height<=480]+bestaudio/best" if is_video else "bestaudio/best"
                with yt_dlp.YoutubeDL({"quiet": True, "format": format_str}) as ydl:
                    return ydl.extract_info(link, download=False).get('url')
            
            try:
                direct_url = await loop.run_in_executor(None, extract_direct_url)
                if direct_url: return direct_url, False
            except: pass

        # ⚡ REGULAR DOWNLOAD (Chunk mode for Zero Error)
        try:
            res = await _core_download(link, is_video)
            return (res, True) if res else (None, False)
        except:
            return None, False
