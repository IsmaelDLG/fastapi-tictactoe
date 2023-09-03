"""
Moves are Game dependant, therefore this resource is a sub-resource of Game.
However, for clarity/cleaness sake, I will implement the Move logic here
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime
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
        closed_at = datetime.utcnow()

    return closed_at, winner_id


def find_winner_inner(board, x, y, last_pid=None, streak=0, current_dir=None):
    # condition 1
    if x < 0 or y < 0 or x > 2 or y > 2:
        return (None, None)
    i = x * 3 + y
    # condition 2
    if board[i] is None:
        return (None, None)
    print(f"x: {x} y: {y} last: {last_pid} id: {board[i]}")
    if last_pid is not None:
        if last_pid == board[i]:
            streak = streak + 1
            print(f"streak: {streak}")
            # condition victory
            if streak == 2:
                return (datetime.utcnow(), board[i])
        # condition 3
        else:
            # bad path, cut branch
            return (None, None)

    closed_at = None
    winner_id = None

    # no direction set, test all
    if current_dir is None:
        for x2, y2 in (
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
                board, x + x2, y + y2, board[i], streak, (x2, y2)
            )
            if closed_at is not None and winner_id is not None:
                return closed_at, winner_id
    else:
        # direction is set, we must go forward
        return find_winner_inner(
            board, x + current_dir[0], y + current_dir[1], board[i], streak, current_dir
        )

    # it's a draw
    return (None, None)


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
