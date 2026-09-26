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
from SIMPLE_MUSIC.utils.formatters import time_to_seconds
import aiohttp
from SIMPLE_MUSIC import LOGGER

API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = "downloads"

from SIMPLE_MUSIC import LOGGER
from SIMPLE_MUSIC.utils.formatters import time_to_seconds

async def download_song(link: str) -> str:
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None
from config import API_URL, VIDEO_API_URL, API_KEY, YT_API_KEY, YTPROXY_URL

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
CLIENT_SESSION = None

    if os.path.exists(file_path):
        return file_path
async def get_session():
    global CLIENT_SESSION
    if CLIENT_SESSION is None or CLIENT_SESSION.closed:
        CLIENT_SESSION = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0))
    return CLIENT_SESSION

async def _download_stream(url, path, headers=None):
try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "audio"}

            async with session.get(
                f"{API_URL}/download",
                params=params,
                timeout=aiohttp.ClientTimeout(total=7)
            ) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                download_token = data.get("download_token")

                if not download_token:
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=audio&token={download_token}"

                async with session.get(
                    stream_url,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as file_response:
                    if file_response.status == 302:
                        redirect_url = file_response.headers.get('Location')
                        if redirect_url:
                            async with session.get(redirect_url) as final_response:
                                if final_response.status != 200:
                                    return None
                                with open(file_path, "wb") as f:
                                    async for chunk in final_response.content.iter_chunked(16384):
                                        f.write(chunk)
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
                                else:
                                    return None
                    elif file_response.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in file_response.content.iter_chunked(16384):
                                f.write(chunk)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            return file_path
                        else:
                            return None
                    else:
                        return None

    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return None
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
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path):
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "video"}

            async with session.get(
                f"{API_URL}/download",
                params=params,
                timeout=aiohttp.ClientTimeout(total=7)
            ) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                download_token = data.get("download_token")

                if not download_token:
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=video&token={download_token}"

                async with session.get(
                    stream_url,
                    timeout=aiohttp.ClientTimeout(total=600)
                ) as file_response:
                    if file_response.status == 302:
                        redirect_url = file_response.headers.get('Location')
                        if redirect_url:
                            async with session.get(redirect_url) as final_response:
                                if final_response.status != 200:
                                    return None
                                with open(file_path, "wb") as f:
                                    async for chunk in final_response.content.iter_chunked(16384):
                                        f.write(chunk)
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
                                else:
                                    return None
                    elif file_response.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in file_response.content.iter_chunked(16384):
                                f.write(chunk)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            return file_path
                        else:
                            return None
                    else:
                        return None

    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return None
    return await _core_download(link, is_video=True)


class YouTubeAPI:
@@ -175,31 +160,22 @@
self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if videoid: link = self.base + link
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
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for msg in messages:
            for ent in (msg.entities or []):
                if ent.type == MessageEntityType.URL: return (msg.text or msg.caption)[ent.offset : ent.offset + ent.length]
            for ent in (msg.caption_entities or []):
                if ent.type == MessageEntityType.TEXT_LINK: return ent.url
return None

async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
results = VideosSearch(link, limit=1)
for result in (await results.next())["result"]:
title = result["title"]
@@ -210,151 +186,92 @@
return title, duration_min, duration_sec, thumbnail, vidid

async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]
        return (await self.details(link, videoid))[0]

async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]
        return (await self.details(link, videoid))[1]

async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
        return (await self.details(link, videoid))[3]

async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
            res = await download_video(link)
            return (1, res) if res else (0, "Video download failed")
except Exception as e:
return 0, f"Video download error: {e}"

async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
try:
            plist = await Playlist.get(link)
        except:
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
            videos = (await Playlist.get(link)).get("videos") or []
            return [data["id"] for data in videos[:limit] if data and data.get("id")]
        except: return []

async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
results = VideosSearch(link, limit=1)
for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid
            return {"title": result["title"], "link": result["link"], "vidid": result["id"], "duration_min": result["duration"], "thumb": result["thumbnails"][0]["url"].split("?")[0]}, result["id"]

async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            return [{"format": f["format"], "filesize": f.get("filesize"), "format_id": f["format_id"], "ext": f["ext"], "format_note": f.get("format_note"), "yturl": link} for f in ydl.extract_info(link, download=False)["formats"] if "dash" not in str(f.get("format", "")).lower()], link

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
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = (await VideosSearch(link, limit=10).next()).get("result")[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

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
        self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None, title: Union[bool, str] = None,
) -> str:
        if videoid:
            link = self.base + link
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
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception:
            res = await _core_download(link, is_video)
            return (res, True) if res else (None, False)
        except:
return None, False
