import logging
import re

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import modules.weather

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("     websocket")

app = FastAPI()


async def handle_command(data: str) -> str:
    """Обрабатывает команду и возвращает ответ"""

    # Погода
    if data == "Погода":
        return modules.weather.get_weather()

    match = re.search(r"Погода в (.+)", data, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        return modules.weather.get_weather(city)

    # Музыка (будущее)
    match = re.search(r"Включи (.+)", data, re.IGNORECASE)
    if match:
        song = match.group(1).strip()
        return f"Включаю {song}..."

    return f"Команда не распознана: {data}"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Connection open: {websocket.client}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")

            response = await handle_command(data)
            await websocket.send_text(response)

    except WebSocketDisconnect:
        logger.info(f"Connection closed: {websocket.client}")  # клиент отключился
