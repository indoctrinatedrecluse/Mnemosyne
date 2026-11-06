from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationDate(BaseModel):
    year: int = Field(ge=1, le=999_999)
    month: int = Field(ge=1, le=12)


class AssassinationEventV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    world_id: UUID
    schema_version: Literal[1]
    event_type: Literal["political.assassination"]
    simulation_date: SimulationDate
    source_entity_id: UUID | None = None
    target_character_id: UUID
    severity: int = Field(ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    world_id: UUID
    parent_event_id: UUID | None
    event_type: str
    schema_version: int
    simulation_year: int
    simulation_month: int
    severity: int
    source_entity_id: UUID | None
    target_character_id: UUID | None
    status: str
    payload: dict[str, Any]
    created_at: datetime
    duplicate: bool = False
    generated_event_ids: list[UUID] = Field(default_factory=list)


class EventEffectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    effect_index: int
    entity_type: str
    entity_id: UUID
    field_name: str
    before_value: Any
    delta_value: Any
    after_value: Any
