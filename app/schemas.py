from datetime import datetime
from pydantic import BaseModel


class GameBase(BaseModel):
    pass


class GameCreate(GameBase):
    pass


class GameResponse(GameBase):
    id: int
    created_at: datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
