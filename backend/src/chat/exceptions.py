from fastapi import HTTPException, status


class ChatCreationHTTPException(HTTPException):
    def __init__(self: "ChatCreationHTTPException", detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnsubscribedError(Exception):
    pass
