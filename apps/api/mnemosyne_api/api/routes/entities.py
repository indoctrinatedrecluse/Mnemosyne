from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mnemosyne_api.api.schemas.entities import (
    CharacterCreate,
    CharacterRead,
    NationCreate,
    NationRead,
)
from mnemosyne_api.persistence.database import get_db
from mnemosyne_api.persistence.models import Character, Nation, World

router = APIRouter(prefix="/worlds/{world_id}", tags=["world entities"])


def _require_world(session: Session, world_id: UUID) -> None:
    if session.get(World, world_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")


@router.post("/nations", response_model=NationRead, status_code=status.HTTP_201_CREATED)
def create_nation(
    world_id: UUID,
    payload: NationCreate,
    session: Session = Depends(get_db),
) -> Nation:
    _require_world(session, world_id)
    nation = Nation(world_id=world_id, **payload.model_dump())
    session.add(nation)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A nation with this name already exists in the world",
        ) from error
    session.refresh(nation)
    return nation


@router.get("/nations", response_model=list[NationRead])
def list_nations(world_id: UUID, session: Session = Depends(get_db)) -> list[Nation]:
    _require_world(session, world_id)
    statement = select(Nation).where(Nation.world_id == world_id).order_by(Nation.name)
    return list(session.scalars(statement).all())


@router.post("/characters", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
def create_character(
    world_id: UUID,
    payload: CharacterCreate,
    session: Session = Depends(get_db),
) -> Character:
    _require_world(session, world_id)
    nation = session.get(Nation, payload.nation_id)
    if nation is None or nation.world_id != world_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nation not found in world",
        )

    character = Character(world_id=world_id, **payload.model_dump())
    session.add(character)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A character with this name already exists in the world",
        ) from error
    session.refresh(character)
    return character


@router.get("/characters", response_model=list[CharacterRead])
def list_characters(world_id: UUID, session: Session = Depends(get_db)) -> list[Character]:
    _require_world(session, world_id)
    statement = select(Character).where(Character.world_id == world_id).order_by(Character.name)
    return list(session.scalars(statement).all())


@router.get("/characters/{character_id}", response_model=CharacterRead)
def get_character(
    world_id: UUID,
    character_id: UUID,
    session: Session = Depends(get_db),
) -> Character:
    character = session.get(Character, character_id)
    if character is None or character.world_id != world_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found in world",
        )
    return character
