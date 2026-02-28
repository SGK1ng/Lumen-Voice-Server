import logging
import re

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import audio
import modules.weather

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("     websocket")

app = FastAPI()


async def handle_command(data: str) -> bytes:
    """Обрабатывает команду и возвращает ответ"""
    data = data.lower()
    # Погода
    if data == "погода":
        return await audio.stream_edge_tts(modules.weather.get_weather())

    match = re.search(r"погода в (.+)", data, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        return await audio.stream_edge_tts(modules.weather.get_weather(city))

    # # Музыка (будущее)
    # match = re.search(r"Включи (.+)", data, re.IGNORECASE)
    # if match:
    #     song = match.group(1).strip()
    #     return f"Включаю {song}..."

    return await audio.stream_edge_tts(f"Команда не распознана: {data}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Connection open: {websocket.client}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")

            pcm = await handle_command(data)
            await websocket.send_bytes(pcm)

    except WebSocketDisconnect:
        logger.info(f"Connection closed: {websocket.client}")  # клиент отключился
