import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
import aiohttp

API_URL = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
API_KEY = os.environ.get("SHRUTI_API_KEY", "YOUR_API_KEY")

DOWNLOAD_DIR = "downloads"

_session: aiohttp.ClientSession = None

async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
        _session = aiohttp.ClientSession(connector=connector)
    return _session


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


async def get_stream_url(link: str, media_type: str = "audio") -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
    
    # 1. Try External API
    try:
        session = await get_session()
        async with session.get(
            f"{API_URL}/download",
            params={"url": video_id, "type": media_type, "api_key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=15)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, dict) and data.get("url"):
                    return data.get("url")
    except Exception:
        pass

    # 2. Local yt-dlp Fallback (For 18+ / Age-Restricted Bypass)
    try:
        url = f"https://www.youtube.com/watch?v={video_id}" if "youtube.com" not in link and "youtu.be" not in link else link
        opts = {
            "format": "bestaudio/best" if media_type == "audio" else "best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "age_limit": 99,
        }
        if os.path.exists("cookies.txt"):
            opts["cookiefile"] = "cookies.txt"

        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("url")
        return await loop.run_in_executor(None, _extract)
    except Exception:
        return None


async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    # 1. Try External API
    try:
        session = await get_session()
        async with session.get(
            f"{API_URL}/download",
            params={"url": video_id, "type": "audio", "api_key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            if resp.status == 200:
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(262144):
                        f.write(chunk)
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return file_path
    except Exception:
        pass

    # 2. Local yt-dlp Fallback for 18+ Videos
    try:
        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "age_limit": 99,
        }
        if os.path.exists("cookies.txt"):
            opts["cookiefile"] = "cookies.txt"

        url = f"https://www.youtube.com/watch?v={video_id}"
        loop = asyncio.get_event_loop()
        def _dl():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        await loop.run_in_executor(None, _dl)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    # 1. Try External API
    try:
        session = await get_session()
        async with session.get(
            f"{API_URL}/download",
            params={"url": video_id, "type": "video", "api_key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            if resp.status == 200:
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(262144):
                        f.write(chunk)
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return file_path
    except Exception:
        pass

    # 2. Local yt-dlp Fallback for 18+ Videos
    try:
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": file_path,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "age_limit": 99,
        }
        if os.path.exists("cookies.txt"):
            opts["cookiefile"] = "cookies.txt"

        url = f"https://www.youtube.com/watch?v={video_id}"
        loop = asyncio.get_event_loop()
        def _dl():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        await loop.run_in_executor(None, _dl)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if res and res.get("result"):
                result = res["result"][0]
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                vidid = result["id"]
                duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
                return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            pass

        # Fallback to yt-dlp if py_yt fails on 18+ links
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "age_limit": 99,
            }
            if os.path.exists("cookies.txt"):
                opts["cookiefile"] = "cookies.txt"

            loop = asyncio.get_event_loop()
            def _info():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(link, download=False)
            info = await loop.run_in_executor(None, _info)
            if info:
                title = info.get("title", "Audio/Video")
                dur = info.get("duration", 0)
                duration_sec = int(dur) if dur else 0
                m, s = divmod(duration_sec, 60)
                duration_min = f"{m}:{s:02d}"
                thumbnail = info.get("thumbnail", "")
                vidid = info.get("id", link)
                return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            pass

        return None, "0:00", 0, "", ""

    async def title(self, link: str, videoid: Union[bool, str] = None):
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, duration_min, _, _, _ = await self.details(link, videoid)
        return duration_min

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        title, duration_min, _, thumbnail, vidid = await self.details(link, videoid)
        track_details = {
            "title": title,
            "link": self.base + vidid if vidid else link,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "age_limit": 99,
        }
        if os.path.exists("cookies.txt"):
            ytdl_opts["cookiefile"] = "cookies.txt"

        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r.get("formats", []):
                try:
                    if "dash" not in str(format.get("format", "")).lower():
                        formats_available.append(
                            {
                                "format": format.get("format"),
                                "filesize": format.get("filesize"),
                                "format_id": format.get("format_id"),
                                "ext": format.get("ext"),
                                "format_note": format.get("format_note"),
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def stream_link(self, link: str, video: bool = False, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        media_type = "video" if video else "audio"
        return await get_stream_url(link, media_type)

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            return None, False
        except Exception:
            return None, False


YouTube = YouTubeAPI()
