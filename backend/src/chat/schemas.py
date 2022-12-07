from pydantic import BaseModel, root_validator

from .service import ChatType, MessageType


class ParticipantCreate(BaseModel):
    id: int
    is_admin: bool = False


class ParticipantRead(BaseModel):
    participant_id: int
    is_admin: bool

    class Config:
        orm_mode = True


class ChatBase(BaseModel):
    type: ChatType


class ChatCreate(ChatBase):
    name: str | None
    participants: list[ParticipantCreate]
    image_url: str | None

    @root_validator
    def check_name(cls, values: dict):
        name, chat_type = values.get("name"), values.get("type")
        if chat_type == ChatType.group:
            assert name, "name should be specified for group chats"
        return values


class ChatRead(ChatBase):
    id: int
    name: str | None
    image_url: str | None
    participants: list[ParticipantRead]

    class Config:
        orm_mode = True


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

    class Config:
        orm_mode = True
        use_enum_values = True
