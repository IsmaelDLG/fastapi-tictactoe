from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import db, schemas, models, oauth2


router = APIRouter(prefix="/games", tags=["Games"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameResponse
)
def create(game: schemas.GameCreate, db: Session = Depends(db.get_db), current_user: str = Depends(oauth2.get_current_user)):
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


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.GameResponse
)
def get_one(id:int, db: Session = Depends(db.get_db)):
    game = db.query(models.Game).filter(models.Game.id == id).first()
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"game with id: {id} was not found")
    
    return game

@router.put(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.GameResponse
)
def update(updated_game: schemas.GameCreate, id:int, db: Session = Depends(db.get_db), current_user: str = Depends(oauth2.get_current_user)):
    game_query = db.query(models.Game).filter(models.Game.id == id)
    current_game = game_query.first() 
    if current_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"game with id: {id} was not found")
    
    for player in (updated_game.player1_id, updated_game.player2_id):
        if db.query(models.User).filter(models.User.id == player).count() != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"player with id: {player} does not exist")

    # update game
    game_query.update(updated_game.model_dump(),synchronize_session=False)
    db.commit()
    db.refresh(current_game)
    return current_game

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(db.get_db), current_user: str = Depends(oauth2.get_current_user)):
    game_query = (
        db.query(models.Game)
        .filter(models.Game.id == id)
    )
    game = game_query.first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )
    
    game_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

