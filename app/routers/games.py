from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .. import db, schemas, models


router = APIRouter(prefix="/games", tags=["Games"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameResponse
)
def create(game: schemas.GameCreate, db: Session = Depends(db.get_db)):
    new_game = models.Game(**game.model_dump())
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.GameResponse]
)
def get_all(db: Session = Depends(db.get_db)):
    return db.query(models.Game).all()
