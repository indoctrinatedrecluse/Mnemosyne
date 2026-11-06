import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mnemosyne_api.main import app
from mnemosyne_api.persistence import models  # noqa: F401
from mnemosyne_api.persistence.base import Base
from mnemosyne_api.persistence.database import get_db


@pytest.fixture
def test_sessions():
    test_engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(test_engine)

    yield TestingSessionLocal

    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def client(test_sessions):
    def override_get_db():
        with test_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
