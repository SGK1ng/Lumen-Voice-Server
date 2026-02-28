import asyncio
import socket

import edge_tts

VOICE_RU = "ru-RU-DmitryNeural"


def is_connected() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


async def convert_to_pcm(input_bytes: bytes, input_format: str = "mp3") -> bytes:
    """Конвертирует аудио в PCM через ffmpeg"""
    ffmpeg = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-f",
        input_format,
        "-i",
        "pipe:0",
        "-f",
        "s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    pcm, _ = await ffmpeg.communicate(input=input_bytes)
    return pcm


async def stream_edge_tts(text: str):
    """Собирает mp3 от edge-tts и отдаёт PCM"""
    communicate = edge_tts.Communicate(text, voice=VOICE_RU)
    mp3_buffer = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_buffer += chunk["data"]
    return await convert_to_pcm(mp3_buffer, "mp3")


async def stream_from_file(filepath: str, input_format: str = "wav") -> bytes:
    """Конвертирует любой файл в PCM"""
    with open(filepath, "rb") as f:
        data = f.read()
    return await convert_to_pcm(data, input_format)
