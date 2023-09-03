from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


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
    player2_id: int


# class GameUpdate(GameCreate):
#     player1_id: int


class GamePatch(GameBase):
    closed_at: Optional[datetime] = None
    winner_id: Optional[int] = None


class GameResponse(GameBase):
    id: int
    created_at: datetime
    player1: UserResponse
    player2: UserResponse
    closed_at: Optional[datetime] = None
    winner_id: Optional[int] = None


class MoveBase(BaseModel):
    position: int


class MoveCreate(MoveBase):
    pass


class MoveResponse(MoveCreate):
    id: int
    player_id: int


class GameAndMoves(BaseModel):
    game: GameResponse
    moves: List[MoveResponse]


class LoginData(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    user_id: int


class TokenResponse(BaseModel):
    token: str
    type: str
