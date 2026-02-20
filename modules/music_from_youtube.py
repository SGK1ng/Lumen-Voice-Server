# import yt_dlp
import subprocess

import yt_dlp
from googleapiclient.discovery import build

from .config import YOUTUBE_API_KEY


def get_url(video_name: str) -> str:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet", type="video", q=video_name, maxResults=1
    )

    response = request.execute()
    url = f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"

    return url


def get_audio(url: str):
    ydl_opts = {"format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(url, download=False)

    audio_url = next(i["url"] for i in song_info["formats"] if i["format_id"] == "140")

    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-i", audio_url, "-f", "wav", "pipe:1", "-loglevel", "quiet"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    return ffmpeg.stdout, ffmpeg
