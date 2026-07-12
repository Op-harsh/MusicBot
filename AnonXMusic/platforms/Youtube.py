import asyncio
import base64
import glob
import os
import random
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from AnonXMusic import LOGGER
from AnonXMusic.utils.formatters import time_to_seconds

logger = LOGGER(__name__)


def setup_cookies():
    """Create cookies file from COOKIES_DATA environment variable (base64 encoded)."""
    cookies_data = os.environ.get("COOKIES_DATA")
    if cookies_data:
        os.makedirs("cookies", exist_ok=True)
        cookie_path = os.path.join("cookies", "youtube_cookies.txt")
        try:
            decoded = base64.b64decode(cookies_data)
            with open(cookie_path, "wb") as f:
                f.write(decoded)
            logger.info("Cookies file created from COOKIES_DATA env variable")
        except Exception as e:
            logger.error(f"Failed to decode cookies: {e}")


# Auto-setup cookies when module loads
setup_cookies()


def cookie_txt_file():
    try:
        folder_path = f"{os.getcwd()}/cookies"
        filename = f"{os.getcwd()}/cookies/logs.csv"
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        if not txt_files:
            raise FileNotFoundError("No .txt files found in the specified folder.")
        cookie_txt_file = random.choice(txt_files)
        with open(filename, "a") as file:
            file.write(f"Choosen File : {cookie_txt_file}\n")
        return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""
    except:
        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _get_ytdlp_opts(self, extra_opts=None):
        """Build base yt-dlp options."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        cookie = cookie_txt_file()
        if cookie:
            opts["cookiefile"] = cookie
        if extra_opts:
            opts.update(extra_opts)
        return opts

    async def _extract_info(self, link, extra_opts=None):
        """Extract video/search info using yt-dlp (non-blocking)."""
        loop = asyncio.get_running_loop()
        opts = self._get_ytdlp_opts(extra_opts)

        def _extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(link, download=False)

        return await loop.run_in_executor(None, _extract)

    async def _search(self, query, limit=1):
        """Search YouTube using yt-dlp and return results."""
        search_query = f"ytsearch{limit}:{query}"
        info = await self._extract_info(search_query)
        entries = info.get("entries", [])
        return entries

    @staticmethod
    def _format_duration(seconds):
        """Convert seconds to M:SS or H:MM:SS format."""
        if not seconds:
            return "0:00"
        seconds = int(seconds)
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"

    @staticmethod
    def _get_thumbnail(info):
        """Get best thumbnail URL from video info."""
        thumb = info.get("thumbnail", "")
        if not thumb:
            thumbnails = info.get("thumbnails", [])
            if thumbnails:
                thumb = thumbnails[-1].get("url", "")
        # Remove query params for clean URL
        if thumb and "?" in thumb:
            thumb = thumb.split("?")[0]
        return thumb

    def _clean_link(self, link):
        """Clean YouTube URL by removing tracking params."""
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
        return link

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                info = await self._extract_info(link)
            else:
                results = await self._search(link, limit=1)
                if not results:
                    raise ValueError("No results found")
                info = results[0]

            title = info.get("title", "Unknown")
            duration_sec = int(info.get("duration", 0) or 0)
            duration_min = self._format_duration(duration_sec)
            thumbnail = self._get_thumbnail(info)
            vidid = info.get("id", "")
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            logger.error(f"Error getting details: {e}")
            raise

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                info = await self._extract_info(link)
            else:
                results = await self._search(link, limit=1)
                if not results:
                    raise ValueError("No results found")
                info = results[0]
            return info.get("title", "Unknown")
        except Exception as e:
            logger.error(f"Error getting title: {e}")
            raise

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                info = await self._extract_info(link)
            else:
                results = await self._search(link, limit=1)
                if not results:
                    raise ValueError("No results found")
                info = results[0]
            duration_sec = int(info.get("duration", 0) or 0)
            return self._format_duration(duration_sec)
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            raise

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                info = await self._extract_info(link)
            else:
                results = await self._search(link, limit=1)
                if not results:
                    raise ValueError("No results found")
                info = results[0]
            return self._get_thumbnail(info)
        except Exception as e:
            logger.error(f"Error getting thumbnail: {e}")
            raise

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        link = self._clean_link(link)
        try:
            info = await self._extract_info(
                link, {"extract_flat": "in_playlist", "playlistend": limit}
            )
            if not info or "entries" not in info:
                return None
            videos = []
            for entry in info["entries"][:limit]:
                try:
                    dur = entry.get("duration")
                    duration_sec = int(dur) if dur else 0
                    duration_min = self._format_duration(duration_sec)
                    vid_id = entry.get("id", "")
                    thumb = entry.get("thumbnails", [{}])[0].get("url", "") if entry.get("thumbnails") else ""
                    if not thumb and vid_id:
                        thumb = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
                    videos.append(
                        {
                            "vidid": vid_id,
                            "title": entry.get("title", "Unknown"),
                            "duration_min": duration_min,
                            "duration_sec": duration_sec,
                            "thumbnail": thumb.split("?")[0] if thumb else "",
                        }
                    )
                except:
                    continue
            return videos
        except Exception as e:
            logger.error(f"Error getting playlist: {e}")
            return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                info = await self._extract_info(link)
            else:
                results = await self._search(link, limit=1)
                if not results:
                    raise ValueError("No results found")
                info = results[0]

            title = info.get("title", "Unknown")
            duration_min = self._format_duration(int(info.get("duration", 0) or 0))
            vidid = info.get("id", "")
            yturl = info.get("webpage_url", self.base + vidid)
            thumbnail = self._get_thumbnail(info)

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }
            return track_details, vidid
        except Exception as e:
            logger.error(f"Error getting track: {e}")
            raise

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            info = await self._extract_info(link)
            formats_available = []
            for fmt in info.get("formats", []):
                try:
                    fmt_str = fmt.get("format", "")
                    if "dash" in fmt_str.lower():
                        continue
                    if not all(
                        fmt.get(k) is not None
                        for k in ["format", "filesize", "format_id", "ext", "format_note"]
                    ):
                        continue
                    formats_available.append(
                        {
                            "format": fmt["format"],
                            "filesize": fmt["filesize"],
                            "format_id": fmt["format_id"],
                            "ext": fmt["ext"],
                            "format_note": fmt["format_note"],
                            "yturl": link,
                        }
                    )
                except:
                    continue
            return formats_available, link
        except Exception as e:
            logger.error(f"Error getting formats: {e}")
            raise

    async def slider(
        self, link: str, query_type: int, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            if re.search(self.regex, link):
                results = await self._search(link, limit=10)
            else:
                results = await self._search(link, limit=10)

            # Filter videos longer than 1 hour
            filtered = []
            for r in results:
                dur = int(r.get("duration", 0) or 0)
                if dur <= 3600:
                    filtered.append(r)

            if not filtered or query_type >= len(filtered):
                raise ValueError("No suitable videos found within duration limit")

            selected = filtered[query_type]
            title = selected.get("title", "Unknown")
            duration = self._format_duration(int(selected.get("duration", 0) or 0))
            thumbnail = self._get_thumbnail(selected)
            vidid = selected.get("id", "")

            return title, duration, thumbnail, vidid

        except Exception as e:
            logger.error(f"Error in slider: {e}")
            raise ValueError("Failed to fetch video details")

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
            vid_id = link
            link = self.base + link
        loop = asyncio.get_running_loop()

        def _get_dl_opts(format_opt, outtmpl, is_audio=False, audio_quality="128"):
            """Build yt-dlp download options."""
            opts = {
                "format": format_opt,
                "outtmpl": outtmpl,
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "retries": 3,
                "fragment_retries": 3,
                "socket_timeout": 30,
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android_creator", "mediaconnect"],
                    }
                },
            }
            if is_audio:
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": audio_quality,
                    }
                ]
            else:
                opts["merge_output_format"] = "mp4"

            cookie = cookie_txt_file()
            if cookie:
                opts["cookiefile"] = cookie
            return opts

        def _audio_dl(vid_id, link):
            """Download audio using yt-dlp directly."""
            filepath = os.path.join("downloads", f"{vid_id}.mp3")
            if os.path.exists(filepath):
                return filepath
            opts = _get_dl_opts(
                "bestaudio/best",
                os.path.join("downloads", f"{vid_id}.%(ext)s"),
                is_audio=True,
                audio_quality="128",
            )
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([link])
                if os.path.exists(filepath):
                    return filepath
            except Exception as e:
                logger.error(f"yt-dlp audio download error: {e}")
            return None

        def _video_dl(vid_id, link):
            """Download video using yt-dlp directly."""
            filepath = os.path.join("downloads", f"{vid_id}.mp4")
            if os.path.exists(filepath):
                return filepath
            opts = _get_dl_opts(
                "best[height<=?720][width<=?1280]/best",
                os.path.join("downloads", f"{vid_id}.%(ext)s"),
            )
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([link])
                if os.path.exists(filepath):
                    return filepath
            except Exception as e:
                logger.error(f"yt-dlp video download error: {e}")
            return None

        def _song_audio_dl(link, title):
            """Download song audio using yt-dlp directly."""
            filepath = os.path.join("downloads", f"{title}.mp3")
            if os.path.exists(filepath):
                return filepath
            opts = _get_dl_opts(
                "bestaudio/best",
                os.path.join("downloads", f"{title}.%(ext)s"),
                is_audio=True,
                audio_quality="320",
            )
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([link])
                if os.path.exists(filepath):
                    return filepath
            except Exception as e:
                logger.error(f"yt-dlp song audio download error: {e}")
            return None

        def _song_video_dl(link, title):
            """Download song video using yt-dlp directly."""
            filepath = os.path.join("downloads", f"{title}.mp4")
            if os.path.exists(filepath):
                return filepath
            opts = _get_dl_opts(
                "best[height<=?720][width<=?1280]/best",
                os.path.join("downloads", f"{title}.%(ext)s"),
            )
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([link])
                if os.path.exists(filepath):
                    return filepath
            except Exception as e:
                logger.error(f"yt-dlp song video download error: {e}")
            return None

        os.makedirs("downloads", exist_ok=True)

        if songvideo:
            fpath = await loop.run_in_executor(None, _song_video_dl, link, title)
            return fpath
        elif songaudio:
            fpath = await loop.run_in_executor(None, _song_audio_dl, link, title)
            return fpath
        elif video:
            direct = True
            downloaded_file = await loop.run_in_executor(
                None, _video_dl, vid_id, link
            )
        else:
            direct = True
            downloaded_file = await loop.run_in_executor(
                None, _audio_dl, vid_id, link
            )

        return downloaded_file, direct
