from fastapi import HTTPException, WebSocket, status
from sqlalchemy import select
from src.auth.models import User
from src.database import AsyncSession

from .models import Chat, ChatParticipant, Message
from .schemas import MessageCreate, MessageRead


async def send_error(websocket: WebSocket, error: dict):
    await websocket.send_json({"error": error})


async def create_message(
    message: dict,
    user: User,
    session: AsyncSession
) -> MessageRead:
    message = MessageCreate(**message)

    # make sure chat exists and user is a participant
    query = select(Chat.id).where(
        Chat.id == message.chat_id,
        ChatParticipant.participant_id == user.id
    )
    result = await session.execute(query)
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    message_data = message.dict()
    message_data.update({
        "author_id": user.id,
        "sender_id": user.id
    })
    new_message = Message(**message_data)

    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)

    return MessageRead.from_orm(new_message)
