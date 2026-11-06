from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Index, SmallInteger, String, Text
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
