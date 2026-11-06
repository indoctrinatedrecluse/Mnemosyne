from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Keep seeds within JavaScript's exact integer range for the desktop client.
MAX_SEED = 9_007_199_254_740_991


class WorldCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2_000)
    seed: int = Field(ge=0, le=MAX_SEED)
    calendar_start_year: int = Field(default=1, ge=1, le=999_999)
    calendar_start_month: int = Field(default=1, ge=1, le=12)
    tick_interval_seconds: int = Field(default=5, ge=1, le=86_400)

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value


class WorldUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2_000)
    seed: int | None = Field(default=None, ge=0, le=MAX_SEED)
    calendar_start_year: int | None = Field(default=None, ge=1, le=999_999)
    calendar_start_month: int | None = Field(default=None, ge=1, le=12)
    tick_interval_seconds: int | None = Field(default=None, ge=1, le=86_400)

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, value: Any) -> Any:
        if isinstance(value, dict):
            for field in (
                "name",
                "seed",
                "calendar_start_year",
                "calendar_start_month",
                "tick_interval_seconds",
            ):
                if field in value and value[field] is None:
                    raise ValueError(f"{field} cannot be null")
        return value

    @model_validator(mode="after")
    def require_a_change(self) -> "WorldUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class WorldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    seed: int
    calendar_start_year: int
    calendar_start_month: int
    tick_interval_seconds: int
    created_at: datetime
    updated_at: datetime
