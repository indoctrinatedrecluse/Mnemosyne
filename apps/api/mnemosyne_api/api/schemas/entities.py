from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    government_type: str = Field(default="Unknown", min_length=1, max_length=80)
    stability: int = Field(default=70, ge=0, le=100)
    unrest: int = Field(default=15, ge=0, le=100)

    @field_validator("name", "government_type", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class NationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    world_id: UUID
    name: str
    government_type: str
    stability: int
    unrest: int
    created_at: datetime
    updated_at: datetime


class CharacterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nation_id: UUID
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(default="Citizen", min_length=1, max_length=120)

    @field_validator("name", "role", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    world_id: UUID
    nation_id: UUID
    name: str
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
