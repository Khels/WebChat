from pydantic import BaseModel


class ClientErrorResponse(BaseModel):
    detail: str
