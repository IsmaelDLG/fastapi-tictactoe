"""
Moves are Game dependant, therefore this resource is a sub-resource of Game.
However, for clarity/cleaness sake, I will implement the Move logic here
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime
from .. import db, schemas, models, oauth2, logs

logger = logs.get_logger(__name__)


router = APIRouter(prefix="/games", tags=["Games"])


def is_valid_move(game, current_moves, player_id, position):
    logger.info(
        f"closed_at: {game.closed_at} n_moves: {len(current_moves)} last_playerid: {current_moves[-1].player_id if len(current_moves) else game.player2_id} playerid: {player_id} position: {position}"
    )
    return (
        game.closed_at is None
        and (
            current_moves[-1].player_id != player_id
            if len(current_moves)
            else player_id == game.player1_id
        )  # is player turn
    ) and (
        position in range(9)
        and all(position != x.position for x in current_moves)  # is valid move
    )


def find_winner(board):
    closed_at = None
    winner_id = None
    nones = 0
    for i in range(len(board)):
        if board[i] is None:
            nones += 1
        (closed_at, winner_id) = find_winner_inner(board, int(i / 3), i % 3)
        if closed_at is not None:
            break

    if nones == 0:
        logger.debug(f"draw")
        closed_at = datetime.utcnow()

    return closed_at, winner_id


def find_winner_inner(board, x, y, last_pid=None, path=()):
    closed_at = None
    winner_id = None

    if x >= 0 and y >= 0 and x <= 2 and y <= 2:
        i = x * 3 + y
        pid = board[i]
        if pid is not None:
            if last_pid is None:
                for dx, dy in (
                    (0, -1),
                    (1, -1),
                    (1, 0),
                    (1, 1),
                    (0, 1),
                    (-1, 1),
                    (-1, 0),
                    (-1, -1),
                ):
                    # board is 3x3, these are the surrounding cells
                    (closed_at, winner_id) = find_winner_inner(
                        board, x + dx, y + dy, pid, ((x, y),)
                    )
                    if closed_at is not None and winner_id is not None:
                        break
            elif last_pid == pid:
                dx = x - path[-1][0]
                dy = y - path[-1][1]
                path += ((x, y),)
                # condicion ganadora
                if len(path) == 3:
                    logger.debug(f"path: {path} found winner!")
                    return (datetime.utcnow(), pid)
                else:
                    (closed_at, winner_id) = find_winner_inner(
                        board, x + dx, y + dy, pid, path
                    )
    return (closed_at, winner_id)


@router.post("/{id}/moves", response_model=schemas.GameAndMoves)
def create_move(
    id: int,
    move: schemas.MoveCreate,
    db: Session = Depends(db.get_db),
    current_user: str = Depends(oauth2.get_current_user),
):
    logger.debug(f"id: {id} json: {move.model_dump()}")
    game_query = db.query(models.Game).filter(
        models.Game.id == id,
        or_(
            models.Game.player1_id == current_user.id,
            models.Game.player2_id == current_user.id,
        ),
    )
    game = game_query.first()
    if game is None:
        logger.info(f"id: {id} not found error")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"game with id: {id} was not found",
        )

    if game.closed_at is not None:
        logger.info(f"id: {id} game is closed!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"game with id: {id} is closed",
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
    else:
        new_move = models.Move(
            game_id=id, player_id=current_user.id, **move.model_dump()
        )
        db.add(new_move)
        db.commit()
        db.refresh(new_move)
        current_moves.append(new_move)

        board = [None for i in range(9)]
        for move in current_moves:
            board[move.position] = move.player_id
        (closed_at, winner_id) = find_winner(board)

        if closed_at is not None:
            new_game = {
                "id": game.id,
                "created_at": game.created_at,
                "player1_id": game.player1_id,
                "player2_id": game.player2_id,
                "closed_at": closed_at,
                "winner_id": winner_id,
            }
            game_query.update(new_game, synchronize_session=False)
            db.commit()
            db.refresh(game)

        return {"game": game, "moves": current_moves}
