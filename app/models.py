import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    username = sa.Column(sa.String, unique=True, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Game(Base):
    __tablename__ = "games"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    player1_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    player2_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    closed_at = sa.Column(sa.TIMESTAMP(timezone=True))
    winner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])


class Move(Base):
    __tablename__ = "moves"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    game_id = sa.Column(
        sa.Integer, sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    player_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    position = sa.Column(sa.Integer, nullable=False)
