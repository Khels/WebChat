from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router
from .chat.router import router as chat_router
from .config import ALLOWED_ORIGINS

app = FastAPI(
    title="Webchat",
    description="Welcome to Webchat's API documentation! Here you will be able to discover all of the ways you can interact with the Webchat API.",  # noqa: E501
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
