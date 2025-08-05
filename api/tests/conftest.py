import os
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import fakeredis

from app.main import app
from app.shared.database import get_db
from app.core.config import settings


@pytest.fixture(scope="session")
def test_settings():
    return settings


@pytest.fixture(scope="session")
def test_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def test_session_local(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def test_db(test_session_local):
    db = test_session_local()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def mock_bike_service():
    mock = Mock()
    mock.get_all_bikes_summary.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 100,
        "pages": 0
    }
    mock.get_bike_history.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 25,
        "pages": 0
    }
    mock.get_current_location.return_value = None
    return mock


@pytest.fixture
def mock_station_service():
    mock = Mock()
    mock.get_all_stations.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 100,
        "pages": 0
    }
    mock.get_station_bikes.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 100,
        "pages": 0
    }
    mock.get_station_stays.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 100,
        "pages": 0
    }
    return mock


@pytest.fixture
def mock_distribution_service():
    mock = Mock()
    mock.get_bike_distribution_by_station.return_value = {
        "total": 0,
        "items": [],
        "page": 1,
        "per_page": 100,
        "pages": 0
    }
    return mock


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("VERSION", "test")