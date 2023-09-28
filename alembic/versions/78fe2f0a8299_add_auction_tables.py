"""Add auction tables

Revision ID: 78fe2f0a8299
Revises: cb51bb611dcb
Create Date: 2023-09-28 15:53:07.994098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "78fe2f0a8299"
down_revision: Union[str, None] = "cb51bb611dcb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "auction",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("bidding_starts_at", sa.DateTime(), nullable=False),
        sa.Column("bidding_ends_at", sa.DateTime(), nullable=False),
        sa.Column("payment_starts_at", sa.DateTime(), nullable=False),
        sa.Column("payment_ends_at", sa.DateTime(), nullable=False),
        sa.Column("sponsored_starts_at", sa.DateTime(), nullable=False),
        sa.Column("sponsored_ends_at", sa.DateTime(), nullable=False),
        sa.Column("sponsored_slots", sa.Integer(), nullable=False),
        sa.Column("minimum_bid", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "bidding_ends_at > bidding_starts_at",
            name="auction_bidding_ends_at_after_bidding_starts_at",
        ),
        sa.CheckConstraint(
            "minimum_bid > 0", name="auction_minimum_bid_greater_than_zero"
        ),
        sa.CheckConstraint(
            "payment_ends_at > payment_starts_at",
            name="auction_payment_ends_at_after_payment_starts_at",
        ),
        sa.CheckConstraint(
            "sponsored_ends_at > sponsored_starts_at",
            name="auction_sponsored_ends_at_after_sponsored_starts_at",
        ),
        sa.CheckConstraint(
            "sponsored_slots > 0", name="auction_sponsored_slots_greater_than_zero"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", name="auction_unique_id"),
    )
    op.create_table(
        "auction_bid",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("auction_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("server_id", sa.UUID(), nullable=False),
        sa.Column("server_name", sa.Text(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="auction_bid_amount_greater_than_zero"),
        sa.ForeignKeyConstraint(
            ["auction_id"], ["auction.id"], name="auction_bid_auction_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["server_id"], ["server.id"], name="auction_bid_server_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name="auction_bid_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", name="auction_bid_unique_id"),
    )
    op.create_table(
        "sponsor",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("server_id", sa.UUID(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "ends_at > starts_at", name="sponsor_ends_at_after_starts_at"
        ),
        sa.ForeignKeyConstraint(
            ["server_id"], ["server.id"], name="sponsor_server_id_fkey"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="sponsor_user_id_fkey"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", name="sponsor_unique_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sponsor")
    op.drop_table("auction_bid")
    op.drop_table("auction")
    # ### end Alembic commands ###
