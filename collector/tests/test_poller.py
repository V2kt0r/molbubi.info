"""
Comprehensive tests for Poller service covering all edge cases.
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.services.poller import Poller
from app.schemas.nextbike import ApiResponse


class TestPoller:
    """Test cases for Poller class."""

    def test_init_default_stream_name(self, api_client, redis_client, mock_settings):
        """Test Poller initialization with default stream name."""
        poller = Poller(api_client=api_client, redis_client=redis_client)
        
        assert poller.api_client == api_client
        assert poller.redis_client == redis_client
        assert poller.stream_name == mock_settings.REDIS_STREAM_NAME

    def test_init_custom_stream_name(self, api_client, redis_client):
        """Test Poller initialization with custom stream name."""
        custom_stream = "custom_test_stream"
        poller = Poller(
            api_client=api_client,
            redis_client=redis_client,
            stream_name=custom_stream
        )
        
        assert poller.stream_name == custom_stream

    def test_poll_and_store_data_success(self, poller, valid_nextbike_data, caplog_info):
        """Test successful polling and storing cycle."""
        # Mock API client to return valid data
        poller.api_client.fetch_bike_data = MagicMock(return_value=valid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify API was called
        poller.api_client.fetch_bike_data.assert_called_once()
        
        # Verify Redis storage was called with validated data
        poller.redis_client.add_to_stream.assert_called_once()
        call_args = poller.redis_client.add_to_stream.call_args
        assert call_args[0][0] == "test_stream"  # stream name
        
        # Verify logging
        assert "Starting data polling cycle" in caplog_info.text
        assert "Data validation successful" in caplog_info.text
        assert "Data polling cycle finished successfully" in caplog_info.text

    def test_poll_and_store_data_no_data_fetched(self, poller, caplog_info):
        """Test handling when API client returns None."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=None)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify API was called
        poller.api_client.fetch_bike_data.assert_called_once()
        
        # Verify Redis storage was NOT called
        poller.redis_client.add_to_stream.assert_not_called()
        
        # Verify logging
        assert "Starting data polling cycle" in caplog_info.text
        assert "No data fetched. Skipping this cycle" in caplog_info.text

    def test_poll_and_store_data_empty_data(self, poller, caplog_info):
        """Test handling when API client returns empty data."""
        poller.api_client.fetch_bike_data = MagicMock(return_value={})
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify API was called
        poller.api_client.fetch_bike_data.assert_called_once()
        
        # Verify Redis storage was NOT called (empty data treated as None)
        poller.redis_client.add_to_stream.assert_not_called()
        
        # Verify logging
        assert "No data fetched. Skipping this cycle" in caplog_info.text

    def test_poll_and_store_data_validation_error_invalid_structure(self, poller, caplog_error):
        """Test handling of validation error with invalid data structure."""
        # This will cause a validation error because countries should be a list, not a string
        invalid_data = {
            "countries": "not_a_list"
        }
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=invalid_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify API was called
        poller.api_client.fetch_bike_data.assert_called_once()
        
        # Verify Redis storage was NOT called
        poller.redis_client.add_to_stream.assert_not_called()
        
        # Verify error logging
        assert "Data validation failed" in caplog_error.text

    def test_poll_and_store_data_validation_error_invalid_types(self, poller, invalid_nextbike_data, caplog_error):
        """Test handling of validation error with invalid data types."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=invalid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify Redis storage was NOT called
        poller.redis_client.add_to_stream.assert_not_called()
        
        # Verify error logging
        assert "Data validation failed" in caplog_error.text

    def test_poll_and_store_data_validation_error_missing_fields(self, poller, caplog_error):
        """Test handling of validation error with missing required fields."""
        data_missing_fields = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    # Missing required fields: uid, lat, lng, name, spot
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=data_missing_fields)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify Redis storage was NOT called
        poller.redis_client.add_to_stream.assert_not_called()
        
        # Verify error logging
        assert "Data validation failed" in caplog_error.text

    def test_poll_and_store_data_minimal_valid_data(self, poller, minimal_nextbike_data, caplog_info):
        """Test handling of minimal valid data."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=minimal_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify API was called
        poller.api_client.fetch_bike_data.assert_called_once()
        
        # Verify Redis storage was called
        poller.redis_client.add_to_stream.assert_called_once()
        
        # Verify logging
        assert "Data validation successful" in caplog_info.text
        assert "Data polling cycle finished successfully" in caplog_info.text

    def test_poll_and_store_data_large_dataset(self, poller, large_nextbike_data, caplog_info):
        """Test handling of large dataset."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=large_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify successful processing
        poller.api_client.fetch_bike_data.assert_called_once()
        poller.redis_client.add_to_stream.assert_called_once()
        
        # Verify the data passed to Redis contains all stations
        call_args = poller.redis_client.add_to_stream.call_args
        stored_data = call_args[0][1]  # Second argument is the data
        assert len(stored_data["countries"][0]["cities"][0]["places"]) == 100

    def test_poll_and_store_data_unicode_data(self, poller, caplog_info):
        """Test handling of data with unicode characters."""
        unicode_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 12345,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Állomás étkezde 🚲",
                                    "spot": False,
                                    "bike_list": [
                                        {"number": "测试123"},
                                        {"number": "vélo456"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=unicode_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify successful processing
        poller.redis_client.add_to_stream.assert_called_once()
        assert "Data validation successful" in caplog_info.text

    def test_poll_and_store_data_redis_error(self, poller, valid_nextbike_data, caplog_info):
        """Test handling when Redis storage fails."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=valid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock(side_effect=Exception("Redis error"))
        
        # Redis errors should propagate up to the main loop
        with pytest.raises(Exception, match="Redis error"):
            poller.poll_and_store_data()
        
        # Verify validation was successful before the Redis error
        assert "Data validation successful" in caplog_info.text

    def test_poll_and_store_data_api_client_exception(self, poller, caplog_info):
        """Test handling when API client raises exception."""
        poller.api_client.fetch_bike_data = MagicMock(side_effect=Exception("API error"))
        poller.redis_client.add_to_stream = MagicMock()
        
        # Should not raise exception, let it propagate to main loop
        with pytest.raises(Exception, match="API error"):
            poller.poll_and_store_data()
        
        # Verify Redis was not called
        poller.redis_client.add_to_stream.assert_not_called()

    def test_poll_and_store_data_mixed_valid_invalid_stations(self, poller, caplog_error):
        """Test handling of mixed valid and invalid station data."""
        mixed_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 12345,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Valid Station",
                                    "spot": False,
                                    "bike_list": []
                                },
                                {
                                    "uid": "invalid",  # Invalid type
                                    "lat": 47.6,
                                    "lng": 19.1,
                                    "name": "Invalid Station",
                                    "spot": False,
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=mixed_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Should fail validation due to invalid station
        poller.redis_client.add_to_stream.assert_not_called()
        assert "Data validation failed" in caplog_error.text

    def test_poll_and_store_data_validation_with_extra_fields(self, poller, caplog_info):
        """Test validation handles extra fields gracefully."""
        data_with_extra_fields = {
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
                                    "spot": False,
                                    "bike_list": [],
                                    "extra_field": "should be ignored",
                                    "another_extra": 123
                                }
                            ]
                        }
                    ]
                }
            ],
            "extra_root_field": "should also be ignored"
        }
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=data_with_extra_fields)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Should succeed with extra fields
        poller.redis_client.add_to_stream.assert_called_once()
        assert "Data validation successful" in caplog_info.text

    def test_poll_and_store_data_stream_name_used_correctly(self, api_client, redis_client, valid_nextbike_data):
        """Test that custom stream name is used correctly."""
        custom_stream = "my_custom_stream"
        poller = Poller(
            api_client=api_client,
            redis_client=redis_client,
            stream_name=custom_stream
        )
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=valid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        poller.poll_and_store_data()
        
        # Verify custom stream name was used
        poller.redis_client.add_to_stream.assert_called_once()
        call_args = poller.redis_client.add_to_stream.call_args
        assert call_args[0][0] == custom_stream

    def test_poll_and_store_data_model_dump_called(self, poller, valid_nextbike_data):
        """Test that model_dump is called on validated data."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=valid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        with patch.object(ApiResponse, 'model_dump') as mock_model_dump:
            mock_model_dump.return_value = {"dumped": "data"}
            
            poller.poll_and_store_data()
            
            # Verify model_dump was called
            mock_model_dump.assert_called_once()
            
            # Verify dumped data was passed to Redis
            call_args = poller.redis_client.add_to_stream.call_args
            assert call_args[0][1] == {"dumped": "data"}

    def test_poll_and_store_data_logging_levels(self, poller, valid_nextbike_data):
        """Test that appropriate logging levels are used."""
        import logging
        
        poller.api_client.fetch_bike_data = MagicMock(return_value=valid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        with patch('app.services.poller.logger') as mock_logger:
            poller.poll_and_store_data()
            
            # Verify info level logging was used
            assert mock_logger.info.call_count == 3
            mock_logger.info.assert_any_call("Starting data polling cycle...")
            mock_logger.info.assert_any_call("Data validation successful.")
            mock_logger.info.assert_any_call("Data polling cycle finished successfully.")

    def test_poll_and_store_data_error_logging_level(self, poller, invalid_nextbike_data):
        """Test that error logging level is used for validation failures."""
        poller.api_client.fetch_bike_data = MagicMock(return_value=invalid_nextbike_data)
        poller.redis_client.add_to_stream = MagicMock()
        
        with patch('app.services.poller.logger') as mock_logger:
            poller.poll_and_store_data()
            
            # Verify error level logging was used
            mock_logger.error.assert_called_once()
            error_call_args = mock_logger.error.call_args[0][0]
            assert "Data validation failed" in error_call_args

    def test_dependency_injection(self):
        """Test that dependencies are properly injected and stored."""
        mock_api_client = MagicMock()
        mock_redis_client = MagicMock()
        custom_stream = "injection_test"
        
        poller = Poller(
            api_client=mock_api_client,
            redis_client=mock_redis_client,
            stream_name=custom_stream
        )
        
        assert poller.api_client is mock_api_client
        assert poller.redis_client is mock_redis_client
        assert poller.stream_name == custom_stream