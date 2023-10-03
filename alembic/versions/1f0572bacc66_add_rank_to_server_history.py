"""add rank to server_history

Revision ID: 1f0572bacc66
Revises: 7bf67b7be656
Create Date: 2023-10-02 22:37:25.992740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, text


# revision identifiers, used by Alembic.
revision: str = "1f0572bacc66"
down_revision: Union[str, None] = "7bf67b7be656"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("server_history", sa.Column("rank", sa.Integer(), nullable=True))
    # ### end Alembic commands ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    session.execute(text("UPDATE server_history SET rank = 1"))

    session.commit()
    session.close()

    op.alter_column("server_history", "rank", nullable=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("server_history", "rank")
    # ### end Alembic commands ###
