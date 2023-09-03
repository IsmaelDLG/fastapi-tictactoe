"""
Moves are Game dependant, therefore this resource is a sub-resource of Game.
However, for clarity/cleaness sake, I will implement the Move logic here
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .. import db, schemas, models, oauth2


router = APIRouter(prefix="/games", tags=["Games"])


def is_valid_move(game, current_moves, player_id, position):
    return (
        game.closed_at is None
        and current_moves[-1].player_id != player_id  # is player turn
    ) and (
        position in range(9)
        and all(position != x.position for x in current_moves)  # is valid move
    )


def find_winner(moves):
    pass


@router.post("/{id}/moves", response_model=schemas.GameAndMoves)
def create_move(
    id: int,
    move: schemas.MoveCreate,
    db: Session = Depends(db.get_db),
    current_user: str = Depends(oauth2.get_current_user),
):
    game_query = db.query(models.Game).filter(
        models.Game.id == id,
        or_(
            models.Game.player1_id == current_user.id,
            models.Game.player2_id == current_user.id,
        ),
        models.Game.closed_at == None,
    )
    game = game_query.first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )

    current_moves = (
        db.query(models.Move)
        .filter(models.Move.game_id == game.id)
        .order_by(models.Move.id)
        .all()
    )

    if not is_valid_move(game, current_moves, current_user.id, move.position):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid move"
        )

    new_move = models.Move(game_id=id, player_id=current_user.id, **move.model_dump())
    db.add(new_move)
    db.commit()
    db.refresh(new_move)
    current_moves.append(new_move)

    (closed_at, player1_won) = find_winner(current_moves)

    if closed_at is not None:
        new_game = {
            "id": game.id,
            "created_at": game.created_at,
            "player1_id": game.player1_id,
            "player2_id": game.player2_id,
            "closed_at": closed_at,
            "player1_won": player1_won,
        }
        game_query.update(new_game, synchronize_session=False)
        db.commit()
        db.refresh(game)

    return {"game": game, "moves": current_moves}
