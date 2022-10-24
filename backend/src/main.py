from fastapi import FastAPI

from .auth.router import router as auth_router

app = FastAPI(
    title="Webchat",
    description="Welcome to Webchat's API documentation! Here you will able to discover all of the ways you can interact with the Webchat API.",  # noqa: E501
)

app.include_router(auth_router)


# @app.on_event("startup")
# async def startup():
#     await db.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}
