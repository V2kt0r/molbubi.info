"""
Comprehensive tests for Redis client covering all edge cases.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
import redis
import fakeredis

from app.storage.redis_client import RedisClient


class TestRedisClient:
    """Test cases for RedisClient class."""

    def test_init_default_params(self, mock_settings):
        """Test RedisClient initialization with default parameters."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            client = RedisClient()
            
            mock_redis.assert_called_once_with(
                host=mock_settings.REDIS_HOST,
                port=mock_settings.REDIS_DOCKER_PORT,
                decode_responses=True
            )
            mock_redis.return_value.ping.assert_called_once()

    def test_init_custom_params(self):
        """Test RedisClient initialization with custom parameters."""
        custom_host = "custom-redis.example.com"
        custom_port = 6380
        
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            client = RedisClient(host=custom_host, port=custom_port)
            
            mock_redis.assert_called_once_with(
                host=custom_host,
                port=custom_port,
                decode_responses=True
            )

    def test_init_connection_success(self, caplog_info):
        """Test successful Redis connection with logging."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            client = RedisClient(host="localhost", port=6379)
            
            assert "Connected to Redis successfully" in caplog_info.text

    def test_init_connection_failure(self, caplog_error):
        """Test Redis connection failure."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.side_effect = redis.ConnectionError("Connection failed")
            
            with pytest.raises(redis.ConnectionError):
                RedisClient(host="localhost", port=6379)
            
            assert "Could not connect to Redis" in caplog_error.text

    def test_init_redis_exception_propagated(self):
        """Test that Redis exceptions are properly propagated."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.side_effect = redis.AuthenticationError("Auth failed")
            
            with pytest.raises(redis.ConnectionError):
                RedisClient(host="localhost", port=6379)

    def test_add_to_stream_success(self, redis_client, caplog_info):
        """Test successful data addition to Redis stream."""
        test_data = {"test": "data", "number": 123}
        stream_name = "test_stream"
        
        redis_client.add_to_stream(stream_name, test_data)
        
        # Verify data was added to stream
        stream_entries = redis_client.client.xrange(stream_name)
        assert len(stream_entries) == 1
        
        # Verify the data structure
        entry_id, entry_data = stream_entries[0]
        assert "data" in entry_data
        stored_data = json.loads(entry_data["data"])
        assert stored_data == test_data
        
        assert f"Added data to stream '{stream_name}'" in caplog_info.text

    def test_add_to_stream_complex_data(self, redis_client):
        """Test adding complex nested data to stream."""
        complex_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 12345,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Test Station",
                                    "bike_list": [
                                        {"number": "123"},
                                        {"number": "456"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        redis_client.add_to_stream("complex_stream", complex_data)
        
        # Verify complex data was stored correctly
        stream_entries = redis_client.client.xrange("complex_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == complex_data

    def test_add_to_stream_unicode_data(self, redis_client):
        """Test adding data with unicode characters."""
        unicode_data = {
            "station_name": "Állomás étkezde",
            "description": "测试站点",
            "emoji": "🚲",
            "special_chars": "àáâãäåæçèéêë"
        }
        
        redis_client.add_to_stream("unicode_stream", unicode_data)
        
        # Verify unicode data was stored correctly
        stream_entries = redis_client.client.xrange("unicode_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == unicode_data
        assert stored_data["station_name"] == "Állomás étkezde"
        assert stored_data["emoji"] == "🚲"

    def test_add_to_stream_large_data(self, redis_client):
        """Test adding large dataset to stream."""
        # Create a large dataset
        large_data = {
            "stations": [
                {
                    "uid": i,
                    "name": f"Station {i}",
                    "bikes": [f"bike_{i}_{j}" for j in range(20)]
                }
                for i in range(100)
            ]
        }
        
        redis_client.add_to_stream("large_stream", large_data)
        
        # Verify large data was stored
        stream_entries = redis_client.client.xrange("large_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert len(stored_data["stations"]) == 100
        assert len(stored_data["stations"][0]["bikes"]) == 20

    def test_add_to_stream_empty_data(self, redis_client):
        """Test adding empty data to stream."""
        empty_data = {}
        
        redis_client.add_to_stream("empty_stream", empty_data)
        
        stream_entries = redis_client.client.xrange("empty_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == {}

    def test_add_to_stream_none_values(self, redis_client):
        """Test adding data with None values."""
        data_with_none = {
            "value1": None,
            "value2": "not_none",
            "nested": {
                "inner_none": None,
                "inner_value": 42
            }
        }
        
        redis_client.add_to_stream("none_stream", data_with_none)
        
        stream_entries = redis_client.client.xrange("none_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == data_with_none
        assert stored_data["value1"] is None

    def test_add_to_stream_special_characters(self, redis_client):
        """Test adding data with special characters in stream name."""
        test_data = {"test": "data"}
        special_stream_names = [
            "stream:with:colons",
            "stream-with-dashes",
            "stream_with_underscores",
            "stream.with.dots",
            "stream123with456numbers"
        ]
        
        for stream_name in special_stream_names:
            redis_client.add_to_stream(stream_name, test_data)
            
            # Verify data was added
            stream_entries = redis_client.client.xrange(stream_name)
            assert len(stream_entries) == 1

    def test_add_to_stream_redis_error(self, caplog_error):
        """Test error handling when Redis operation fails."""
        mock_redis = MagicMock()
        mock_redis.xadd.side_effect = redis.RedisError("Redis operation failed")
        
        with patch('redis.Redis', return_value=mock_redis):
            client = RedisClient(host="localhost", port=6379)
            client.add_to_stream("error_stream", {"test": "data"})
        
        assert "Error adding data to Redis stream" in caplog_error.text

    def test_add_to_stream_connection_error(self, caplog_error):
        """Test error handling when Redis connection fails during operation."""
        mock_redis = MagicMock()
        mock_redis.xadd.side_effect = redis.ConnectionError("Connection lost")
        
        with patch('redis.Redis', return_value=mock_redis):
            client = RedisClient(host="localhost", port=6379)
            client.add_to_stream("connection_error_stream", {"test": "data"})
        
        assert "Error adding data to Redis stream" in caplog_error.text

    def test_add_to_stream_timeout_error(self, caplog_error):
        """Test error handling when Redis operation times out."""
        mock_redis = MagicMock()
        mock_redis.xadd.side_effect = redis.TimeoutError("Operation timed out")
        
        with patch('redis.Redis', return_value=mock_redis):
            client = RedisClient(host="localhost", port=6379)
            client.add_to_stream("timeout_stream", {"test": "data"})
        
        assert "Error adding data to Redis stream" in caplog_error.text

    def test_add_to_stream_json_serialization_error(self, caplog_error):
        """Test error handling when JSON serialization fails."""
        # Create data that can't be JSON serialized
        class UnserializableClass:
            pass
        
        unserialized_data = {"object": UnserializableClass()}
        
        with patch('redis.Redis'):
            client = RedisClient(host="localhost", port=6379)
            client.add_to_stream("json_error_stream", unserialized_data)
        
        assert "Error adding data to Redis stream" in caplog_error.text

    def test_add_to_stream_multiple_calls(self, redis_client):
        """Test multiple calls to add_to_stream create separate entries."""
        stream_name = "multi_stream"
        
        for i in range(5):
            redis_client.add_to_stream(stream_name, {"sequence": i})
        
        # Verify all entries were added
        stream_entries = redis_client.client.xrange(stream_name)
        assert len(stream_entries) == 5
        
        # Verify entries are in correct order
        for i, (entry_id, entry_data) in enumerate(stream_entries):
            stored_data = json.loads(entry_data["data"])
            assert stored_data["sequence"] == i

    def test_add_to_stream_numeric_data_types(self, redis_client):
        """Test adding various numeric data types."""
        numeric_data = {
            "integer": 42,
            "float": 3.14159,
            "negative": -123,
            "zero": 0,
            "large_number": 999999999999999,
            "scientific": 1.23e-10
        }
        
        redis_client.add_to_stream("numeric_stream", numeric_data)
        
        stream_entries = redis_client.client.xrange("numeric_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == numeric_data

    def test_add_to_stream_boolean_data(self, redis_client):
        """Test adding boolean data types."""
        boolean_data = {
            "true_value": True,
            "false_value": False,
            "nested": {
                "inner_true": True,
                "inner_false": False
            }
        }
        
        redis_client.add_to_stream("boolean_stream", boolean_data)
        
        stream_entries = redis_client.client.xrange("boolean_stream")
        assert len(stream_entries) == 1
        
        entry_id, entry_data = stream_entries[0]
        stored_data = json.loads(entry_data["data"])
        assert stored_data == boolean_data
        assert stored_data["true_value"] is True
        assert stored_data["false_value"] is False

    def test_client_instance_reuse(self, fake_redis):
        """Test that Redis client instance is properly reused."""
        with patch('redis.Redis', return_value=fake_redis) as mock_redis:
            client = RedisClient(host="localhost", port=6379)
            
            # Make multiple calls
            client.add_to_stream("stream1", {"data": 1})
            client.add_to_stream("stream2", {"data": 2})
            
            # Redis should only be instantiated once
            mock_redis.assert_called_once()
            
            # Both streams should exist
            assert fake_redis.exists("stream1")
            assert fake_redis.exists("stream2")