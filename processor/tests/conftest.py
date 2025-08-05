"""
Shared test fixtures and configuration for processor service tests.
"""
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import fakeredis
import logging

# Set up test environment variables before importing app modules
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_DOCKER_PORT", "6379")
os.environ.setdefault("REDIS_STREAM_NAME", "test_stream")
os.environ.setdefault("REDIS_CONSUMER_GROUP", "test_group")
os.environ.setdefault("REDIS_CONSUMER_NAME", "test_consumer")
os.environ.setdefault("REDIS_BIKE_STATE_HASH", "test_bike_states")
os.environ.setdefault("REDIS_STATION_BIKES_SET_PREFIX", "test_station_bikes")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test_db")

from app.core.config import settings
from app.schemas.bike_data import ApiResponse, Country, City, Station, Bike, BikeState


# Logging fixtures
@pytest.fixture
def caplog_info(caplog):
    """Capture INFO level logs."""
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture
def caplog_error(caplog):
    """Capture ERROR level logs."""
    caplog.set_level(logging.ERROR)
    return caplog


@pytest.fixture
def caplog_warning(caplog):
    """Capture WARNING level logs."""
    caplog.set_level(logging.WARNING)
    return caplog


# Configuration fixtures
@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return settings


# Database fixtures  
@pytest.fixture
def test_db_engine():
    """Create a test database engine using SQLite in memory."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    return engine


@pytest.fixture  
def test_db_session(test_db_engine):
    """Create a test database session."""
    # Use the actual shared models from our created module
    from shared_models.models import Base, Station, BikeMovement, BikeStay
    
    # Create tables
    Base.metadata.create_all(test_db_engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Redis fixtures
@pytest.fixture
def fake_redis():
    """Create a fake Redis client for testing."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def redis_client(fake_redis):
    """Create a Redis client fixture."""
    return fake_redis


# Sample data fixtures
@pytest.fixture
def sample_bike():
    """Sample bike data."""
    return Bike(number="BIKE123")


@pytest.fixture
def sample_station():
    """Sample station data."""
    return Station(
        uid=1001,
        lat=47.5,
        lng=19.0,
        name="Test Station",
        spot=True,
        bike_list=[Bike(number="BIKE123"), Bike(number="BIKE456")]
    )


@pytest.fixture
def sample_station_without_bikes():
    """Sample station without bikes."""
    return Station(
        uid=1002,
        lat=47.6,
        lng=19.1,
        name="Empty Station",
        spot=True,
        bike_list=[]
    )


@pytest.fixture
def sample_city():
    """Sample city data."""
    return City(places=[
        Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Test Station 1",
            spot=True,
            bike_list=[Bike(number="BIKE123")]
        ),
        Station(
            uid=1002,
            lat=47.6,
            lng=19.1,
            name="Test Station 2",
            spot=True,
            bike_list=[Bike(number="BIKE456")]
        )
    ])


@pytest.fixture
def sample_country():
    """Sample country data."""
    return Country(cities=[
        City(places=[
            Station(
                uid=1001,
                lat=47.5,
                lng=19.0,
                name="Test Station 1",
                spot=True,
                bike_list=[Bike(number="BIKE123")]
            ),
            Station(
                uid=1002,
                lat=47.6,
                lng=19.1,
                name="Test Station 2",
                spot=True,
                bike_list=[Bike(number="BIKE456")]
            )
        ])
    ])


@pytest.fixture
def sample_api_response():
    """Sample API response data."""
    return ApiResponse(countries=[
        Country(cities=[
            City(places=[
                Station(
                    uid=1001,
                    lat=47.5,
                    lng=19.0,
                    name="Test Station 1",
                    spot=True,
                    bike_list=[Bike(number="BIKE123")]
                ),
                Station(
                    uid=1002,
                    lat=47.6,
                    lng=19.1,
                    name="Test Station 2",
                    spot=True,
                    bike_list=[Bike(number="BIKE456")]
                )
            ])
        ])
    ])


@pytest.fixture
def minimal_api_response():
    """Minimal valid API response."""
    return ApiResponse(countries=[
        Country(cities=[
            City(places=[
                Station(
                    uid=1001,
                    lat=47.5,
                    lng=19.0,
                    name="Minimal Station",
                    spot=True,
                    bike_list=[]
                )
            ])
        ])
    ])


@pytest.fixture
def large_api_response():
    """Large API response with many stations and bikes."""
    stations = []
    for i in range(50):
        bikes = [Bike(number=f"BIKE{i}_{j}") for j in range(5)]
        stations.append(Station(
            uid=2000 + i,
            lat=47.0 + i * 0.01,
            lng=19.0 + i * 0.01,
            name=f"Station {i}",
            spot=True,
            bike_list=bikes
        ))
    
    return ApiResponse(countries=[
        Country(cities=[City(places=stations)])
    ])


@pytest.fixture
def sample_bike_state():
    """Sample bike state."""
    return BikeState(
        station_uid=1001,
        timestamp=1640995200.0,  # 2022-01-01 00:00:00 UTC
        stay_start_time=1640995200.0
    )


@pytest.fixture
def invalid_api_response_data():
    """Invalid API response data for testing validation errors."""
    return {
        "countries": [
            {
                "cities": [
                    {
                        "places": [
                            {
                                "uid": "invalid_uid",  # Should be int
                                "lat": 47.5,
                                "lng": 19.0,
                                "name": "Invalid Station",
                                "spot": True,
                                "bike_list": []
                            }
                        ]
                    }
                ]
            }
        ]
    }


# Mock Redis stream message fixtures
@pytest.fixture
def sample_redis_message():
    """Sample Redis stream message."""
    return {
        "data": '{"countries": [{"cities": [{"places": [{"uid": 1001, "lat": 47.5, "lng": 19.0, "name": "Test Station", "spot": true, "bike_list": [{"number": "BIKE123"}]}]}]}]}'
    }


@pytest.fixture
def invalid_redis_message():
    """Invalid Redis stream message."""
    return {
        "data": '{"invalid": "json structure"}'
    }


@pytest.fixture
def malformed_redis_message():
    """Malformed JSON Redis message."""
    return {
        "data": '{"countries": [{"cities": [{"places": [{"uid": 1001, "lat": 47.5, "lng":'  # Incomplete JSON
    }