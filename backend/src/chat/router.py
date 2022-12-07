import json
from datetime import datetime

from fastapi import (APIRouter, Depends, HTTPException, Response, WebSocket,
                     WebSocketDisconnect, status)
from fastapi.concurrency import run_until_first_complete
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload, selectinload
from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.auth.schemas import UserRead
from src.auth.utils import authenticate_user_ws
from src.config import REDIS_URL
from src.database import AsyncSession, get_db_session

from .exceptions import ChatCreationHTTPException
from .models import Chat, ChatParticipant
from .schemas import ChatCreate, ChatRead, MessageRead, ParticipantCreate
from .service import Broadcast, ChatType
from .utils import create_message

broadcast = Broadcast(REDIS_URL)

router = APIRouter(
    prefix="/api/v1",
    tags=['chat'],
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)


async def message_receiver(
    websocket: WebSocket,
    user: User,
    session: AsyncSession
):
    while True:
        message = await websocket.receive()
        websocket._raise_on_disconnect(message)
        data = {}

        print(message)

        if message["text"]:
            try:
                message_data = json.loads(message["text"])
                new_message = await create_message(message_data, user, session)
                data = new_message.dict()

                # TODO: notify user message was received by server
                # websocket.send_json({
                #     "flow": MessageFlow.notification,
                #     "content": {

                #     }
                # })
            except ValidationError as e:
                await websocket.send_json({"error": str(e)})
            except HTTPException as e:
                await websocket.send_json({"error": str(e)})
        elif message["bytes"]:
            # TODO process uploaded files
            pass

        data = {
            "content": data,
            "user": UserRead.from_orm(user).dict()
        }
        print(data)
        await broadcast.publish(channel="chatroom",
                                message=json.dumps(data))


async def message_sender(websocket: WebSocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await websocket.send_json(event.message)


@router.websocket("/chat", name="chat")
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
            (message_sender, {
                "websocket": websocket
            }),
            (message_receiver, {
                "websocket": websocket,
                "user": user,
                "session": session
            }),
        )
    except WebSocketDisconnect:
        user.last_online = datetime.utcnow()  # user offline
        await session.commit()


@router.post("/chats")
async def create_chat(
    chat: ChatCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    # make sure chat creator is a participant as well as the admin
    chat_creator_included = False
    for participant in chat.participants:
        if participant.id == user.id:
            participant.is_admin = True
            chat_creator_included = True
            break

    if not chat_creator_included:
        chat.participants.append(ParticipantCreate(id=user.id, is_admin=True))

    print("\n\n\nparticipants: ", chat.participants)

    match chat.type:
        case ChatType.saved_messages:
            query = select(Chat).where(
                Chat.type == ChatType.saved_messages,
                Chat.participants.any(
                    ChatParticipant.participant_id.in_(
                        [p.id for p in chat.participants]
                    )
                )
            )
            result = await session.execute(query)
            if result.scalar():
                raise ChatCreationHTTPException(
                    detail="There is already Saved messages "
                           "chat created for this user."
                )
        case ChatType.dialogue:
            for participant in chat.participants:
                # in a dialogue, both users are admins
                participant.is_admin = True

            # TODO: fix the query
            query = select(Chat).where(
                Chat.type == ChatType.dialogue,
                Chat.participants.any(
                    ChatParticipant.participant_id.in_(
                        [p.id for p in chat.participants]
                    )
                )
            )
            result = await session.execute(query)
            if result.scalar():
                raise ChatCreationHTTPException(
                    detail="There is already a dialogue "
                           "created with this user."
                )

    chat_data = chat.dict()
    chat_data.pop("participants")

    new_chat = Chat(**chat_data)

    session.add(new_chat)

    new_chat.add_participants(chat.participants)
    await session.commit()
    await session.refresh(new_chat)

    return new_chat


@router.get("/chats", response_model=list[ChatRead])
async def get_chats(
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    query = select(Chat).options(
        selectinload(Chat.participants)
    ).where(
        Chat.participants.any(User.id == user.id)
    )
    result = await session.execute(query)

    return result.scalars().all()


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    # TODO: check user permissions
    query = delete(Chat).where(Chat.id == chat_id)
    await session.execute(query)
    await session.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.get("/chats/{chat_id}/messages", response_model=list[MessageRead])
async def get_messages(
    chat_id: int,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    query = select(Chat).options(
        joinedload(Chat.messages)
    ).where(
        Chat.id == chat_id,
        ChatParticipant.participant_id == user.id
    )
    result = await session.execute(query)
    chat = result.scalar()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return chat.messages
