from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mnemosyne_api.api.schemas.events import AssassinationEventV1, EventRead
from mnemosyne_api.persistence.models import (
    Character,
    EventEffect,
    EventRecord,
    Nation,
    World,
)


def _event_response(
    session: Session,
    event: EventRecord,
    *,
    duplicate: bool = False,
) -> EventRead:
    generated_ids = list(
        session.scalars(select(EventRecord.id).where(EventRecord.parent_event_id == event.id)).all()
    )
    return EventRead.model_validate(event).model_copy(
        update={"duplicate": duplicate, "generated_event_ids": generated_ids}
    )


def _idempotent_response(
    session: Session,
    existing: EventRecord,
    payload: AssassinationEventV1,
) -> EventRead:
    canonical_payload = payload.model_dump(mode="json")
    if existing.payload != canonical_payload:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event ID was already used for a different event",
        )
    return _event_response(session, existing, duplicate=True)


def apply_assassination(
    session: Session,
    world_id: UUID,
    payload: AssassinationEventV1,
) -> EventRead:
    if payload.world_id != world_id:
        raise HTTPException(
            status_code=422,
            detail="Event world_id must match the request path",
        )

    existing = session.get(EventRecord, payload.event_id)
    if existing is not None:
        return _idempotent_response(session, existing, payload)

    world = session.get(World, world_id)
    if world is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    character = session.get(Character, payload.target_character_id)
    if character is None or character.world_id != world_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target character not found in world",
        )
    if character.status != "alive":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Target character is already deceased",
        )

    nation = session.get(Nation, character.nation_id)
    if nation is None or nation.world_id != world_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Target character has an invalid nation affiliation",
        )

    canonical_payload = payload.model_dump(mode="json")
    record = EventRecord(
        id=payload.event_id,
        world_id=world_id,
        event_type=payload.event_type,
        schema_version=payload.schema_version,
        simulation_year=payload.simulation_date.year,
        simulation_month=payload.simulation_date.month,
        severity=payload.severity,
        source_entity_id=payload.source_entity_id,
        target_character_id=character.id,
        status="applied",
        payload=canonical_payload,
    )

    old_status = character.status
    old_stability = nation.stability
    old_unrest = nation.unrest
    new_stability = max(0, old_stability - payload.severity)
    new_unrest = min(100, old_unrest + payload.severity)

    follow_up_id = uuid4()
    follow_up = EventRecord(
        id=follow_up_id,
        world_id=world_id,
        parent_event_id=payload.event_id,
        event_type="political.unrest",
        schema_version=1,
        simulation_year=payload.simulation_date.year,
        simulation_month=payload.simulation_date.month,
        severity=payload.severity,
        source_entity_id=character.id,
        target_character_id=None,
        status="pending",
        payload={
            "cause_event_id": str(payload.event_id),
            "nation_id": str(nation.id),
            "trigger": "political.assassination",
        },
    )

    session.add_all(
        [
            record,
            follow_up,
            EventEffect(
                event_id=payload.event_id,
                effect_index=0,
                entity_type="character",
                entity_id=character.id,
                field_name="status",
                before_value=old_status,
                delta_value="alive -> deceased",
                after_value="deceased",
            ),
            EventEffect(
                event_id=payload.event_id,
                effect_index=1,
                entity_type="nation",
                entity_id=nation.id,
                field_name="stability",
                before_value=old_stability,
                delta_value=new_stability - old_stability,
                after_value=new_stability,
            ),
            EventEffect(
                event_id=payload.event_id,
                effect_index=2,
                entity_type="nation",
                entity_id=nation.id,
                field_name="unrest",
                before_value=old_unrest,
                delta_value=new_unrest - old_unrest,
                after_value=new_unrest,
            ),
        ]
    )
    character.status = "deceased"
    nation.stability = new_stability
    nation.unrest = new_unrest

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        existing = session.get(EventRecord, payload.event_id)
        if existing is not None:
            return _idempotent_response(session, existing, payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event could not be applied because of a conflicting state change",
        ) from error

    session.refresh(record)
    return _event_response(session, record)
