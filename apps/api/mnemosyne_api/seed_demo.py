from sqlalchemy import select
from sqlalchemy.orm import Session

from mnemosyne_api.persistence.database import SessionLocal
from mnemosyne_api.persistence.models import World

DEMO_WORLD = {
    "name": "The Shattered Meridian",
    "description": "A small geopolitical world for the first Mnemosyne demo.",
    "seed": 73421,
    "calendar_start_year": 104,
    "calendar_start_month": 1,
    "tick_interval_seconds": 5,
}


def seed_demo_world(session: Session) -> tuple[World, bool]:
    existing = session.scalar(select(World).where(World.name == DEMO_WORLD["name"]))
    if existing is not None:
        return existing, False

    world = World(**DEMO_WORLD)
    session.add(world)
    session.commit()
    session.refresh(world)
    return world, True


def main() -> None:
    with SessionLocal() as session:
        world, created = seed_demo_world(session)
        if created:
            print(f"Created demo world: {world.id}")
        else:
            print(f"Demo world already exists: {world.id}")


if __name__ == "__main__":
    main()
