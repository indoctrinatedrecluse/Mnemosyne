from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from mnemosyne_api.persistence.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class World(Base):
    __tablename__ = "worlds"
    __table_args__ = (
        CheckConstraint("calendar_start_month BETWEEN 1 AND 12", name="ck_worlds_start_month"),
        CheckConstraint("calendar_start_year >= 1", name="ck_worlds_start_year"),
        CheckConstraint("seed >= 0", name="ck_worlds_seed_non_negative"),
        CheckConstraint(
            "tick_interval_seconds BETWEEN 1 AND 86400", name="ck_worlds_tick_interval"
        ),
        Index("ix_worlds_name", "name"),
        Index("ix_worlds_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    calendar_start_year: Mapped[int] = mapped_column(nullable=False, default=1)
    calendar_start_month: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    tick_interval_seconds: Mapped[int] = mapped_column(nullable=False, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class Nation(Base):
    __tablename__ = "nations"
    __table_args__ = (
        CheckConstraint("stability BETWEEN 0 AND 100", name="ck_nations_stability_range"),
        CheckConstraint("unrest BETWEEN 0 AND 100", name="ck_nations_unrest_range"),
        UniqueConstraint("world_id", "name", name="uq_nations_world_name"),
        Index("ix_nations_world_id", "world_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    world_id: Mapped[UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    government_type: Mapped[str] = mapped_column(String(80), nullable=False, default="Unknown")
    stability: Mapped[int] = mapped_column(nullable=False, default=70)
    unrest: Mapped[int] = mapped_column(nullable=False, default=15)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        CheckConstraint("status IN ('alive', 'deceased')", name="ck_characters_status"),
        UniqueConstraint("world_id", "name", name="uq_characters_world_name"),
        Index("ix_characters_world_id", "world_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    world_id: Mapped[UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    nation_id: Mapped[UUID] = mapped_column(
        ForeignKey("nations.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False, default="Citizen")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="alive")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class EventRecord(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("schema_version >= 1", name="ck_events_schema_version"),
        CheckConstraint("simulation_year >= 1", name="ck_events_simulation_year"),
        CheckConstraint("simulation_month BETWEEN 1 AND 12", name="ck_events_simulation_month"),
        CheckConstraint("severity BETWEEN 1 AND 10", name="ck_events_severity"),
        Index("ix_events_world_created_at", "world_id", "created_at"),
        Index("ix_events_parent_event_id", "parent_event_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    world_id: Mapped[UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    parent_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    schema_version: Mapped[int] = mapped_column(nullable=False)
    simulation_year: Mapped[int] = mapped_column(nullable=False)
    simulation_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    severity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    source_entity_id: Mapped[UUID | None] = mapped_column(nullable=True)
    target_character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )


class EventEffect(Base):
    __tablename__ = "event_effects"
    __table_args__ = (
        UniqueConstraint("event_id", "effect_index", name="uq_event_effects_event_index"),
        Index("ix_event_effects_event_id", "event_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    effect_index: Mapped[int] = mapped_column(nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    field_name: Mapped[str] = mapped_column(String(80), nullable=False)
    before_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    delta_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    after_value: Mapped[Any] = mapped_column(JSON, nullable=False)
