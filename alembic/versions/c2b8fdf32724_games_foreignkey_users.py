"""games foreignkey users

Revision ID: c2b8fdf32724
Revises: a42f65fd6d34
Create Date: 2023-09-01 08:36:17.347221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2b8fdf32724"
down_revision: Union[str, None] = "a42f65fd6d34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Como es sqlite3 y no soporte alters ni fantasia, uso estrategia copy-and-move


def upgrade() -> None:
    with op.batch_alter_table("games") as batch_op:
        batch_op.add_column(sa.Column("player1_id", sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column("player2_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_users_id_2", "users", ["player2_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_foreign_key(
            "fk_users_id_1", "users", ["player1_id"], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    with op.batch_alter_table("games") as batch_op:
        batch_op.drop_constraint("fk_users_id_2", type_="foreignkey")
        batch_op.drop_constraint("fk_users_id_1", type_="foreignkey")
        batch_op.drop_column("player2_id")
        batch_op.drop_column("player1_id")
