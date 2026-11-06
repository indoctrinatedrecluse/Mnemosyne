from sqlalchemy import select

from mnemosyne_api.persistence.models import World
from mnemosyne_api.seed_demo import seed_demo_world


def test_demo_seed_is_idempotent(test_sessions):
    with test_sessions() as session:
        first, created_first = seed_demo_world(session)

    with test_sessions() as session:
        second, created_second = seed_demo_world(session)
        worlds = list(session.scalars(select(World)).all())

    assert created_first is True
    assert created_second is False
    assert first.id == second.id
    assert len(worlds) == 1
