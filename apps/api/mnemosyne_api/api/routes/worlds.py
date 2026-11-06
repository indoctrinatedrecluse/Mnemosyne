from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from mnemosyne_api.api.schemas.world import WorldCreate, WorldRead, WorldUpdate
from mnemosyne_api.persistence.database import get_db
from mnemosyne_api.persistence.models import World

router = APIRouter(prefix="/worlds", tags=["worlds"])


@router.post("", response_model=WorldRead, status_code=status.HTTP_201_CREATED)
def create_world(payload: WorldCreate, session: Session = Depends(get_db)) -> World:
    world = World(**payload.model_dump())
    session.add(world)
    session.commit()
    session.refresh(world)
    return world


@router.get("", response_model=list[WorldRead])
def list_worlds(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
) -> list[World]:
    statement = (
        select(World)
        .order_by(World.created_at.desc(), World.name)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement).all())


@router.get("/{world_id}", response_model=WorldRead)
def get_world(world_id: UUID, session: Session = Depends(get_db)) -> World:
    world = session.get(World, world_id)
    if world is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    return world


@router.patch("/{world_id}", response_model=WorldRead)
def update_world(
    world_id: UUID,
    payload: WorldUpdate,
    session: Session = Depends(get_db),
) -> World:
    world = session.get(World, world_id)
    if world is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(world, field, value)

    session.commit()
    session.refresh(world)
    return world
