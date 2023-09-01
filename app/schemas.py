from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime


class GameBase(BaseModel):
    pass


class GameCreate(GameBase):
    player1_id: int
    player2_id: int


class GameResponse(GameBase):
    id: int
    created_at: datetime
    player1: UserResponse
    player2: UserResponse
