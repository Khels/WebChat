import json
from datetime import datetime

from anyio import create_task_group
from fastapi import (APIRouter, Depends, HTTPException, Response, WebSocket,
                     WebSocketDisconnect, status)
from fastapi.websockets import WebSocketState
from pydantic import ValidationError
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import contains_eager, joinedload
from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.auth.utils import authenticate_user_token
from src.config import REDIS_URL
from src.database import AsyncSession, get_db_session
from src.enums import WSError

from .enums import ChatType, WSMessageType
from .exceptions import ChatCreationHTTPException
from .models import Chat, ChatParticipant, Message
from .schemas import (ChatCreate, ChatRead, MessageRead, ParticipantCreate,
                      WSAuthMessage, WSMessage)
from .service import Broadcast
from .utils import create_message, send_error

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
    while websocket.client_state == WebSocketState.CONNECTED:
        message = await websocket.receive()
        websocket._raise_on_disconnect(message)
        msg_type = None
        data = {}

        if message["text"]:
            data = json.loads(message["text"])
            try:
                message_data = WSMessage(**data)

                match message_data.type:
                    case WSMessageType.NOTIFICATION:
                        msg_type = WSMessageType.NOTIFICATION.value
                    case WSMessageType.MESSAGE:
                        msg_type = WSMessageType.MESSAGE.value

                        new_message = await create_message(
                            message_data.dict()["body"], user, session)
                        data = new_message.dict()
            except ValidationError as e:
                await send_error(websocket, e.json())
                continue
            except HTTPException as e:
                await send_error(websocket, str(e))
                continue
        elif message["bytes"]:
            # TODO process uploaded files
            pass

        data = {
            "type": msg_type,
            "body": data,
        }
        print(data)
        await broadcast.publish(channel="chatroom",
                                message=json.dumps(data, default=str))


async def message_sender(websocket: WebSocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            print("\n\n\n", event.message)
            await websocket.send_json(event.message)


@router.websocket("/chat", name="chat")
async def chat(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db_session)
):
    await websocket.accept()

    user = None
    try:
        # wait for the first message with access token
        data = await websocket.receive_json()

        try:
            data = WSAuthMessage(**data)
        except ValidationError as e:
            # send error message with full description
            await send_error(websocket, e.json())
            raise WebSocketDisconnect(
                code=WSError.VALIDATION_ERROR,
                reason=WSError.VALIDATION_ERROR.label
            )

        user = await authenticate_user_token(
            token=data.body.token,
            session=session,
            websocket=websocket
        )

        user.last_online = None  # user online
        await session.commit()

        # TODO notify other participants that user is online

        async with create_task_group() as task_group:
            task_group.start_soon(message_sender, websocket)
            task_group.start_soon(message_receiver, websocket, user, session)
    except WebSocketDisconnect as e:
        if user:
            user.last_online = datetime.utcnow()  # user offline
            await session.commit()
        await websocket.close(code=e.code, reason=e.reason)


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
        case ChatType.SAVED_MESSAGES:
            query = select(Chat).where(
                Chat.type == ChatType.SAVED_MESSAGES,
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
        case ChatType.DIALOGUE:
            for participant in chat.participants:
                # in a dialogue, both users are admins
                participant.is_admin = True

            # TODO: fix the query
            query = select(Chat).where(
                Chat.type == ChatType.DIALOGUE,
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
    subquery = select(Message.id.label("last_message_id")).order_by(
        Message.created_at.desc()
    ).limit(1).scalar_subquery().correlate(Chat)

    query = select(Chat).outerjoin(
        Message, and_(Message.chat_id == Chat.id, Message.id == subquery)
    ).options(
        joinedload(Chat.participants),
        contains_eager(Chat.messages)
    ).where(
        Chat.participants.any(ChatParticipant.participant_id == user.id)
    )

    result = await session.execute(query)

    return result.unique().scalars().all()


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
    limit: int | None = None,
    offset: int | None = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    query = select(Chat).join(Chat.participants).options(
        contains_eager(Chat.participants),
    ).where(
        Chat.id == chat_id,
        ChatParticipant.participant_id == user.id
    )
    result = await session.execute(query)
    chat = result.scalar()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query = select(Message).where(Message.chat_id == chat_id).order_by(
        Message.created_at)
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)
    result = await session.execute(query)
    messages = result.scalars().all()

    return messages
