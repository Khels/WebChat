from enum import StrEnum


class ChatType(StrEnum):
    SAVED_MESSAGES = "saved_messages"
    DIALOGUE = "dialogue"
    GROUP = "group"


class MessageType(StrEnum):
    TEXT = "text"
    VOICE = "voice"
    FILE = "file"


class WSMessageType(StrEnum):
    AUTHENTICATION = "authentication"
    NOTIFICATION = "notification"
    MESSAGE = "message"


class WSNotificationType(StrEnum):
    USER_TYPING = "user_typing"
    USER_STOPPED_TYPING = "user_stopped_typing"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
