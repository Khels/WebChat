import enum


class ChatType(enum.Enum):
    SAVED_MESSAGES = 1
    DIALOGUE = 2
    GROUP = 3


class MessageType(enum.Enum):
    TEXT = 1
    VOICE = 2
    FILE = 3


class WSMessageType(enum.Enum):
    AUTHENTICATION = 1
    NOTIFICATION = 2
    MESSAGE = 3


class WSNotificationType(enum.Enum):
    USER_TYPING = 1
    USER_STOPPED_TYPING = 2
    USER_ONLINE = 3
    USER_OFFLINE = 4
