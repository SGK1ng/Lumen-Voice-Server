import logging
import subprocess

import yt_dlp
from googleapiclient.discovery import build

from .config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)


def get_url(video_name: str) -> str | None:
    """Возвращает URL или None если не найдено"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet", type="video", q=video_name, maxResults=1
    )

    try:
        response = request.execute()
        if not response.get("items"):
            return None  # не найдено

        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"

    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return None  # ошибка API


def get_audio(music_name: str):
    url = get_url(music_name)
    if not url:
        logger.error("No urls found")
        return None

    try:
        ydl_opts = {"format": "bestaudio"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
            song_info = ydl.extract_info(url, download=False)

    except yt_dlp.utils.DownloadError as e:  # type: ignore
        logger.error(f"Download error: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected yt-dlp error: {e}")
        return None

    formats = song_info.get("formats", [])
    if not formats:
        logger.error("No formats available")
        return None

    audio_formats = [
        f for f in formats if f.get("acodec") != "none" and f.get("abr") is not None
    ]

    if not audio_formats:
        logger.error("No audio formats found")
        return None

    best_format = max(audio_formats, key=lambda x: float(x["abr"]))
    audio_url = best_format["url"]

    logger.info(
        f"Selected format: {best_format.get('format_id')} with {best_format['abr']}kbps"
    )

    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-i", audio_url, "-f", "wav", "pipe:1", "-loglevel", "quiet"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    return ffmpeg.stdout, ffmpeg
