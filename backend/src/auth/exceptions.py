from fastapi import HTTPException, status


class InvalidTokenHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided token is invalid",
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenExpiredHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
