from datetime import datetime
from pydantic import BaseModel
from typing import Optional


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
    player1_won: Optional[bool] = None    


class GameResponse(GameBase):
    id: int
    created_at: datetime
    player1: UserResponse
    player2: UserResponse
    closed_at: Optional[datetime] = None
    player1_won: Optional[bool] = None    

class TokenData(BaseModel):
    user_id:int
    
class TokenResponse(BaseModel):
    token:str
    type:str
