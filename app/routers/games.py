from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import db, schemas, models


router = APIRouter(prefix="/games", tags=["Games"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameResponse
)
def create(game: schemas.GameCreate, db: Session = Depends(db.get_db)):
    for player in (game.player1_id, game.player2_id):
        if db.query(models.User).filter(models.User.id == player).count() != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"player with id: {player} does not exist")

    # create game
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
