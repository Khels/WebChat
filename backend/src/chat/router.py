import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from src.config import REDIS_URL

from .service import Broadcast

logger = logging.getLogger(__name__)

broadcast = Broadcast(REDIS_URL)

router = APIRouter(
    prefix="/api/v1",
    tags=['chat'],
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)


async def message_receiver(websocket: WebSocket):
    while True:
        message = await websocket.receive()
        websocket._raise_on_disconnect(message)
        await broadcast.publish(channel="chatroom",
                                message=message["text"])


async def message_sender(websocket: WebSocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


@router.websocket("/chat/", name="chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        await run_until_first_complete(
            (message_sender, {"websocket": websocket}),
            (message_receiver, {"websocket": websocket}),
        )
    except WebSocketDisconnect:
        logger.info(f"Websocket connection {websocket} closed")
