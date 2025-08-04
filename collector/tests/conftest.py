"""
Pytest configuration and shared fixtures for collector service tests.
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch
import fakeredis

# Set up test environment variables before importing app modules
os.environ.setdefault("API_URL", "https://test-api.example.com")
os.environ.setdefault("POLLING_INTERVAL_SECONDS", "10")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_DOCKER_PORT", "6379")
os.environ.setdefault("REDIS_STREAM_NAME", "test_stream")

from app.api.client import ApiClient
from app.storage.redis_client import RedisClient
from app.services.poller import Poller


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('app.core.config.settings') as mock:
        mock.API_URL = "https://test-api.example.com"
        mock.POLLING_INTERVAL_SECONDS = 10
        mock.REDIS_HOST = "localhost"
        mock.REDIS_DOCKER_PORT = 6379
        mock.REDIS_STREAM_NAME = "test_stream"
        yield mock


@pytest.fixture
def fake_redis():
    """Fake Redis client for testing."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def api_client():
    """API client instance for testing."""
    return ApiClient(api_url="https://test-api.example.com", timeout=5)


@pytest.fixture
def redis_client(fake_redis):
    """Redis client with mocked connection."""
    with patch('redis.Redis', return_value=fake_redis):
        client = RedisClient(host="localhost", port=6379)
        client.client = fake_redis
        return client


@pytest.fixture
def poller(api_client, redis_client):
    """Poller service instance for testing."""
    return Poller(
        api_client=api_client,
        redis_client=redis_client,
        stream_name="test_stream"
    )


@pytest.fixture
def valid_nextbike_data():
    """Valid NextBike API response data."""
    return {
        "countries": [
            {
                "cities": [
                    {
                        "places": [
                            {
                                "uid": 42990604,
                                "lat": 47.515002,
                                "lng": 19.039806,
                                "name": "Test Station",
                                "spot": False,
                                "bike_list": [
                                    {"number": "123456"},
                                    {"number": "789012"}
                                ]
                            },
                            {
                                "uid": 42990605,
                                "lat": 47.516002,
                                "lng": 19.040806,
                                "name": "Empty Station",
                                "spot": True,
                                "bike_list": []
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def minimal_nextbike_data():
    """Minimal valid NextBike API response."""
    return {
        "countries": []
    }


@pytest.fixture
def invalid_nextbike_data():
    """Invalid NextBike API response data."""
    return {
        "countries": [
            {
                "cities": [
                    {
                        "places": [
                            {
                                "uid": "invalid_uid",  # Should be int
                                "lat": "invalid_lat",  # Should be float
                                "lng": 19.039806,
                                "name": "Test Station",
                                "spot": False,
                                "bike_list": [
                                    {"number": "123456"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def large_nextbike_data():
    """Large NextBike API response for performance testing."""
    stations = []
    for i in range(100):
        bikes = [{"number": f"{j:06d}"} for j in range(i, i + 10)]
        stations.append({
            "uid": 42990000 + i,
            "lat": 47.5 + (i * 0.001),
            "lng": 19.0 + (i * 0.001),
            "name": f"Station {i}",
            "spot": i % 2 == 0,
            "bike_list": bikes
        })
    
    return {
        "countries": [
            {
                "cities": [
                    {
                        "places": stations
                    }
                ]
            }
        ]
    }


@pytest.fixture
def caplog_info(caplog):
    """Caplog fixture with INFO level."""
    import logging
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture
def caplog_error(caplog):
    """Caplog fixture with ERROR level."""
    import logging
    caplog.set_level(logging.ERROR)
    return caplog


@pytest.fixture
def mock_sleep():
    """Mock asyncio.sleep for faster tests."""
    with patch('asyncio.sleep') as mock:
        yield mock