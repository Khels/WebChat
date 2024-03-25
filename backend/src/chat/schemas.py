from datetime import datetime

from pydantic import BaseModel, Field, model_validator, validator

from .enums import ChatType, MessageType, WSMessageType, WSNotificationType


class ParticipantCreate(BaseModel):
    id: int
    is_admin: bool = False


class ParticipantRead(BaseModel):
    participant_id: int
    is_admin: bool

    class Config:
        orm_mode = True


# ## Message ###
class MessageBase(BaseModel):
    chat_id: int
    type: MessageType
    content: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    author_id: int
    sender_id: int
    is_read: bool
    is_edited: bool
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


# ## Chat ###
class ChatBase(BaseModel):
    type: ChatType


class ChatCreate(ChatBase):
    name: str | None
    participants: list[ParticipantCreate]
    image_url: str | None

    @model_validator(mode="after")
    def check_name(self) -> "ChatCreate":  # noqa: ANN101
        if self.type == ChatType.GROUP:
            assert self.name, "name should be specified for group chats"  # noqa: S101
        return self


class ChatRead(ChatBase):
    id: int
    name: str | None
    image_url: str | None
    participants: list[ParticipantRead]
    messages: list[MessageRead]

    class Config:
        orm_mode = True


# ## Websocket ###
class WSAuthBody(BaseModel):
    token: str = Field(default=..., min_length=64)


class WSNotificationBody(BaseModel):
    type: WSNotificationType
    user_id: int

    class Config:
        extra = "forbid"


class WSMessageBody(MessageCreate):
    class Config:
        extra = "forbid"


class WSMessageBase(BaseModel):
    type: WSMessageType


class WSAuthMessage(WSMessageBase):
    body: WSAuthBody

    @validator("type")
    def check_message_type(cls, value: int) -> int:  # noqa: ANN101, N805
        assert (  # noqa: S101
            value == WSMessageType.AUTHENTICATION
        ), "message type should be set to Authentication"
        return value


class WSMessage(WSMessageBase):
    body: WSNotificationBody | WSMessageBody
