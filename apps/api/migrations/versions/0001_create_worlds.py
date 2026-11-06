"""Create initial worlds table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_worlds"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "worlds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("seed", sa.BigInteger(), nullable=False),
        sa.Column("calendar_start_year", sa.Integer(), nullable=False),
        sa.Column("calendar_start_month", sa.SmallInteger(), nullable=False),
        sa.Column("tick_interval_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("calendar_start_month BETWEEN 1 AND 12", name="ck_worlds_start_month"),
        sa.CheckConstraint("calendar_start_year >= 1", name="ck_worlds_start_year"),
        sa.CheckConstraint("seed >= 0", name="ck_worlds_seed_non_negative"),
        sa.CheckConstraint(
            "tick_interval_seconds BETWEEN 1 AND 86400", name="ck_worlds_tick_interval"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_worlds"),
    )
    op.create_index("ix_worlds_name", "worlds", ["name"], unique=False)
    op.create_index("ix_worlds_created_at", "worlds", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_worlds_created_at", table_name="worlds")
    op.drop_index("ix_worlds_name", table_name="worlds")
    op.drop_table("worlds")
