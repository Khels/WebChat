from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from src.auth.utils import authenticate_user_ws
from src.config import REDIS_URL
from src.database import AsyncSession, get_db_session

from .service import Broadcast

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
        print(message)
        websocket._raise_on_disconnect(message)
        await broadcast.publish(channel="chatroom",
                                message=message["text"])


async def message_sender(websocket: WebSocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


@router.websocket("/chat/", name="chat")
async def chat(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db_session)
):
    await websocket.accept()

    user = await authenticate_user_ws(
        websocket=websocket,
        session=session
    )

    user.last_online = None  # user online
    await session.commit()

    try:
        await run_until_first_complete(
            (message_sender, {"websocket": websocket}),
            (message_receiver, {"websocket": websocket}),
        )
    except WebSocketDisconnect:
        user.last_online = datetime.utcnow()  # user offline
        await session.commit()
