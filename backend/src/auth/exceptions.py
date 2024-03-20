from fastapi import HTTPException, status


class InvalidTokenHTTPException(HTTPException):
    def __init__(self: "InvalidTokenHTTPException") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredHTTPException(HTTPException):
    def __init__(self: "TokenExpiredHTTPException") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
