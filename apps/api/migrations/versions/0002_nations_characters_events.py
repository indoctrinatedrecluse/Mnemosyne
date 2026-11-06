"""Add nations, characters, and event history."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_nations_characters_events"
down_revision: str | None = "0001_create_worlds"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "nations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("government_type", sa.String(length=80), nullable=False),
        sa.Column("stability", sa.Integer(), nullable=False),
        sa.Column("unrest", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("stability BETWEEN 0 AND 100", name="ck_nations_stability_range"),
        sa.CheckConstraint("unrest BETWEEN 0 AND 100", name="ck_nations_unrest_range"),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_nations"),
        sa.UniqueConstraint("world_id", "name", name="uq_nations_world_name"),
    )
    op.create_index("ix_nations_world_id", "nations", ["world_id"], unique=False)

    op.create_table(
        "characters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("nation_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('alive', 'deceased')", name="ck_characters_status"),
        sa.ForeignKeyConstraint(["nation_id"], ["nations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_characters"),
        sa.UniqueConstraint("world_id", "name", name="uq_characters_world_name"),
    )
    op.create_index("ix_characters_world_id", "characters", ["world_id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("parent_event_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("simulation_year", sa.Integer(), nullable=False),
        sa.Column("simulation_month", sa.SmallInteger(), nullable=False),
        sa.Column("severity", sa.SmallInteger(), nullable=False),
        sa.Column("source_entity_id", sa.Uuid(), nullable=True),
        sa.Column("target_character_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("schema_version >= 1", name="ck_events_schema_version"),
        sa.CheckConstraint("simulation_year >= 1", name="ck_events_simulation_year"),
        sa.CheckConstraint("simulation_month BETWEEN 1 AND 12", name="ck_events_simulation_month"),
        sa.CheckConstraint("severity BETWEEN 1 AND 10", name="ck_events_severity"),
        sa.ForeignKeyConstraint(["parent_event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_character_id"], ["characters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_events"),
    )
    op.create_index(
        "ix_events_world_created_at", "events", ["world_id", "created_at"], unique=False
    )
    op.create_index("ix_events_parent_event_id", "events", ["parent_event_id"], unique=False)

    op.create_table(
        "event_effects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("effect_index", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("field_name", sa.String(length=80), nullable=False),
        sa.Column("before_value", sa.JSON(), nullable=False),
        sa.Column("delta_value", sa.JSON(), nullable=False),
        sa.Column("after_value", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_event_effects"),
        sa.UniqueConstraint("event_id", "effect_index", name="uq_event_effects_event_index"),
    )
    op.create_index("ix_event_effects_event_id", "event_effects", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_event_effects_event_id", table_name="event_effects")
    op.drop_table("event_effects")
    op.drop_index("ix_events_parent_event_id", table_name="events")
    op.drop_index("ix_events_world_created_at", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_characters_world_id", table_name="characters")
    op.drop_table("characters")
    op.drop_index("ix_nations_world_id", table_name="nations")
    op.drop_table("nations")
