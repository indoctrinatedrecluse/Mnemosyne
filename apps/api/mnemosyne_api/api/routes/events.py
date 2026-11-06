from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from mnemosyne_api.api.schemas.events import AssassinationEventV1, EventEffectRead, EventRead
from mnemosyne_api.persistence.database import get_db
from mnemosyne_api.persistence.models import EventEffect, EventRecord, World
from mnemosyne_api.services.events import apply_assassination

router = APIRouter(tags=["events"])


@router.post(
    "/worlds/{world_id}/events",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    responses={200: {"model": EventRead, "description": "Previously applied duplicate event"}},
)
def submit_event(
    world_id: UUID,
    payload: AssassinationEventV1,
    response: Response,
    session: Session = Depends(get_db),
) -> EventRead:
    result = apply_assassination(session, world_id, payload)
    if result.duplicate:
        response.status_code = status.HTTP_200_OK
        return result
    return result


@router.get("/worlds/{world_id}/events", response_model=list[EventRead])
def list_world_events(world_id: UUID, session: Session = Depends(get_db)) -> list[EventRead]:
    if session.get(World, world_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    events = session.scalars(
        select(EventRecord)
        .where(EventRecord.world_id == world_id)
        .order_by(EventRecord.created_at.desc(), EventRecord.id)
    ).all()
    responses: list[EventRead] = []
    for event in events:
        generated_ids = list(
            session.scalars(
                select(EventRecord.id).where(EventRecord.parent_event_id == event.id)
            ).all()
        )
        responses.append(
            EventRead.model_validate(event).model_copy(
                update={"generated_event_ids": generated_ids}
            )
        )
    return responses


@router.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: UUID, session: Session = Depends(get_db)) -> EventRead:
    event = session.get(EventRecord, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    generated_ids = list(
        session.scalars(select(EventRecord.id).where(EventRecord.parent_event_id == event.id)).all()
    )
    return EventRead.model_validate(event).model_copy(update={"generated_event_ids": generated_ids})


@router.get("/events/{event_id}/effects", response_model=list[EventEffectRead])
def get_event_effects(event_id: UUID, session: Session = Depends(get_db)) -> list[EventEffect]:
    if session.get(EventRecord, event_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return list(
        session.scalars(
            select(EventEffect)
            .where(EventEffect.event_id == event_id)
            .order_by(EventEffect.effect_index)
        ).all()
    )
