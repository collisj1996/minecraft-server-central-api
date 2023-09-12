"""Add banner url to server

Revision ID: 8ce723b0a06b
Revises: 6c06fe4971a6
Create Date: 2023-09-13 00:22:16.263396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ce723b0a06b'
down_revision: Union[str, None] = '6c06fe4971a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('banner_url', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('server', 'banner_url')
    # ### end Alembic commands ###
