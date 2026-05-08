from pydantic import BaseModel
from datetime import datetime


class InfoCreate(BaseModel):
    key: str
    value: str


class InfoUpdate(BaseModel):
    value: str


class InfoOut(BaseModel):
    id: int
    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True
