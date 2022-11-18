from fastapi import Depends, HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from src.config import ALGORITHM, SECRET_KEY
from src.database import AsyncSession, get_db_session

from .exceptions import CredentialsHTTPException, ExpiredSignatureHTTPException
from .models import User
from .schemas import TokenData
from .service import oauth2_scheme
from .utils import get_user


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsHTTPException()
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        raise ExpiredSignatureHTTPException()
    except JWTError:
        raise CredentialsHTTPException()

    user = await get_user(session, username=token_data.username)
    if user is None:
        raise CredentialsHTTPException()

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
