"""Add vote info to server history

Revision ID: b79cf7b79c42
Revises: d2a9fe23bc2e
Create Date: 2023-10-03 21:23:21.516858

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import orm, text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b79cf7b79c42"
down_revision: Union[str, None] = "d2a9fe23bc2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("server_history", sa.Column("new_votes", sa.Integer(), nullable=True))
    op.add_column(
        "server_history", sa.Column("votes_this_month", sa.Integer(), nullable=True)
    )
    op.add_column(
        "server_history", sa.Column("total_votes", sa.Integer(), nullable=True)
    )
    # ### end Alembic commands ###

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    session.execute(
        text(
            "UPDATE server_history SET new_votes = 0, votes_this_month = 0, total_votes = 0"
        )
    )

    session.commit()
    session.close()

    op.alter_column(
        "server_history",
        "new_votes",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "server_history",
        "votes_this_month",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "server_history",
        "total_votes",
        existing_type=sa.INTEGER(),
        nullable=False,
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("server_history", "total_votes")
    op.drop_column("server_history", "votes_this_month")
    op.drop_column("server_history", "new_votes")
    # ### end Alembic commands ###
