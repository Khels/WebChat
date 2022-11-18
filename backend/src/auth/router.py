from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from src.database import AsyncSession, get_db_session
from src.schemas import ClientErrorResponse

from .dependencies import get_current_active_user
from .models import User
from .schemas import (AccessToken, LoginResponse, RefreshToken, UserCreate,
                      UserRead)
from .utils import (authenticate_user, create_access_token,
                    create_refresh_token, get_password_hash, get_user)

router = APIRouter(prefix="/api/v1", tags=['auth'])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    responses={
        400: {
            "description": "Passwords did not match",
            "model": ClientErrorResponse,
        },
        409: {
            "description": "Username is already taken",
            "model": ClientErrorResponse,
        },
    }
)
async def register(
    user: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    # check if user already exist
    try:
        user = await get_user(session, user.username)
    except HTTPException:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken"
        )

    # compare passwords
    if user.password != user.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Passwords do not match'
        )

    # hash the password
    user.password = get_password_hash(user.password)
    del user.password_confirm

    # non-model fields
    user_dict = user.dict()
    user_dict["is_active"] = True

    new_user = User(**user_dict)

    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {
            "description": "Incorrect username or password",
            "model": ClientErrorResponse,
        }
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session)
):
    user = await authenticate_user(
        session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: make sure user doesn't spam system with login thus creating lots of tokens
    access_token = await create_access_token(
        session=session, user=user, scopes=form_data.scopes)
    refresh_token = await create_refresh_token(
        session=session, user=user, scopes=form_data.scopes)

    print(access_token, access_token.token, access_token.expires, access_token.scopes)
    print(refresh_token, refresh_token.token, refresh_token.expires, refresh_token.scopes)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=UserRead)
async def refresh_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session)
):
    pass


@router.post("/token/revoke")
async def revoke_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session)
):
    pass


# @router.get('/refresh')
# def refresh_token(response: Response, request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
#     try:
#         Authorize.jwt_refresh_token_required()

#         user_id = Authorize.get_jwt_subject()
#         if not user_id:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail='Could not refresh access token')
#         user = db.query(models.User).filter(models.User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail='The user belonging to this token no logger exist')
#         access_token = Authorize.create_access_token(
#             subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
#     except Exception as e:
#         error = e.__class__.__name__
#         if error == 'MissingTokenError':
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=error)

#     response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
#                         ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
#     response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
#                         ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
#     return {'access_token': access_token}


@router.post("/users", response_model=UserRead)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    data = user.dict()
    hashed_password = get_password_hash(data["password"])
    data["password"] = hashed_password
    user = User(**data)

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@router.get("/users/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users", response_model=list[UserRead])
async def users(
    session: AsyncSession = Depends(get_db_session)
):
    results = await session.execute(select(User))
    return results.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
