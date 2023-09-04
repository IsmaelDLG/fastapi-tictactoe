from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .. import db, schemas, models, oauth2, logs

logger = logs.get_logger(__name__)


router = APIRouter(prefix="/games", tags=["Games"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameResponse
)
def create(
    game: schemas.GameCreate,
    db: Session = Depends(db.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """Creates a game with 2 players. Player 1 is set to the authenticated user."""
    logger.debug(f"id: {id} json: {game.model_dump()}")
    if current_user.id == game.player2_id:
        logger.info(
            f"player1_id: {current_user.id} player2_id: {game.player2_id} equal error"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"players must be diffent",
        )

    for player in (current_user.id, game.player2_id):
        if db.query(models.User).filter(models.User.id == player).count() != 1:
            logger.info(f"player: {player} not found error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"player with id: {player} does not exist",
            )

    # create game
    new_game = models.Game(player1_id=current_user.id, **game.model_dump())
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    logger.debug("ok")
    return new_game


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.GameResponse]
)
def get_all(db: Session = Depends(db.get_db), limit: int = 3):
    logger.debug(f"id: {id} limit: {limit}")
    return db.query(models.Game).limit(limit).all()


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.GameResponse
)
def get_one(id: int, db: Session = Depends(db.get_db)):
    logger.debug(f"id: {id}")
    game = db.query(models.Game).filter(models.Game.id == id).first()
    if game is None:
        logger.info("id: {id} not found error")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )

    return game


@router.patch("/{id}")
def patch(
    id: int,
    up_game: schemas.GamePatch,
    db: Session = Depends(db.get_db),
    current_user: str = Depends(oauth2.get_current_user),
):
    logger.debug(f"id: {id} json: {up_game.model_dump()}")
    game_query = db.query(models.Game).filter(
        models.Game.id == id,
        or_(
            models.Game.player1_id == current_user.id,
            models.Game.player2_id == current_user.id,
        ),
    )
    game = game_query.first()
    if game is None:
        logger.info(f"game_id: {id} not found error")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )

    new_game = {
        "id": game.id,
        "created_at": game.created_at,
        "player1_id": game.player1_id,
        "player2_id": game.player2_id,
    }

    if up_game.winner_id is not None:
        if up_game.closed_at is None:
            logger.info(
                f"game_id: {id} winner_id: {up_game.winner_id} closed_at: {up_game.closed_at} can not set winner in open game"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="if winner is defined, closed date must also be defined",
            )
        # both must be set
        new_game["winner_id"] = up_game.winner_id
    new_game["closed_at"] = up_game.closed_at
    game_query.update(new_game, synchronize_session=False)
    db.commit()
    db.refresh(game)
    logger.debug("ok")
    return game


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(db.get_db),
    current_user: str = Depends(oauth2.get_current_user),
):
    logger.debug(f"id: {id}")
    game_query = db.query(models.Game).filter(
        models.Game.id == id,
        or_(
            models.Game.player1_id == current_user.id,
            models.Game.player2_id == current_user.id,
        ),
    )
    game = game_query.first()
    if game is None:
        logger.info("id: {id} not found error")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )

    game_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
