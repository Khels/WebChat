from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import select
from src.database import AsyncSession, get_session


router = APIRouter(tags=['chat'])


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    pass
    # await manager.connect(websocket)
    # try:
    #     while True:
    #         data = await websocket.receive()
    #         await manager.send_personal_message(f"You wrote: {data}", websocket)
    #         await manager.broadcast(f"Client #{client_id} says: {data}")
    # except WebSocketDisconnect:
    #     manager.disconnect(websocket)
    #     await manager.broadcast(f"Client #{client_id} left the chat")
