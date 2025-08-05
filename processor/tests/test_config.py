"""
Comprehensive tests for configuration management covering all edge cases.
"""
import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from app.core.config import Settings, settings


class TestSettings:
    """Test cases for Settings configuration class."""

    def test_settings_initialization_with_env_vars(self):
        """Test settings initialization with environment variables."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "test-redis-host",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream",
            "REDIS_CONSUMER_GROUP": "test_group",
            "REDIS_CONSUMER_NAME": "test_consumer",
            "REDIS_BIKE_STATE_HASH": "test_bike_states",
            "REDIS_STATION_BIKES_SET_PREFIX": "test_station_bikes",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
            "POSTGRES_SERVER": "test_server",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "test_database"
        }):
            test_settings = Settings()
            
            assert test_settings.REDIS_HOST == "test-redis-host"
            assert test_settings.REDIS_DOCKER_PORT == 6380
            assert test_settings.REDIS_STREAM_NAME == "test_stream"
            assert test_settings.REDIS_CONSUMER_GROUP == "test_group"
            assert test_settings.REDIS_CONSUMER_NAME == "test_consumer"
            assert test_settings.REDIS_BIKE_STATE_HASH == "test_bike_states"
            assert test_settings.REDIS_STATION_BIKES_SET_PREFIX == "test_station_bikes"
            assert test_settings.POSTGRES_USER == "test_user"
            assert test_settings.POSTGRES_PASSWORD == "test_password"
            assert test_settings.POSTGRES_SERVER == "test_server"
            assert test_settings.POSTGRES_PORT == 5433
            assert test_settings.POSTGRES_DB == "test_database"

    def test_database_url_property(self):
        """Test database URL property construction."""
        with patch.dict(os.environ, {
            "POSTGRES_USER": "myuser",
            "POSTGRES_PASSWORD": "mypassword",
            "POSTGRES_SERVER": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "mydatabase"
        }):
            test_settings = Settings()
            expected_url = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
            assert test_settings.database_url == expected_url

    def test_database_url_with_special_characters(self):
        """Test database URL with special characters in password."""
        with patch.dict(os.environ, {
            "POSTGRES_USER": "user@domain",
            "POSTGRES_PASSWORD": "pass@word#123",
            "POSTGRES_SERVER": "db.example.com",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "my-database"
        }):
            test_settings = Settings()
            expected_url = "postgresql://user@domain:pass@word#123@db.example.com:5432/my-database"
            assert test_settings.database_url == expected_url

    def test_database_url_with_unicode_characters(self):
        """Test database URL with unicode characters."""
        with patch.dict(os.environ, {
            "POSTGRES_USER": "üser",
            "POSTGRES_PASSWORD": "pássword",
            "POSTGRES_SERVER": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "tëst_db"
        }):
            test_settings = Settings()
            expected_url = "postgresql://üser:pássword@localhost:5432/tëst_db"
            assert test_settings.database_url == expected_url

    def test_redis_port_type_conversion(self):
        """Test that Redis port is properly converted to integer."""
        with patch.dict(os.environ, {"REDIS_DOCKER_PORT": "6379"}):
            test_settings = Settings()
            assert isinstance(test_settings.REDIS_DOCKER_PORT, int)
            assert test_settings.REDIS_DOCKER_PORT == 6379

    def test_postgres_port_type_conversion(self):
        """Test that PostgreSQL port is properly converted to integer."""
        with patch.dict(os.environ, {"POSTGRES_PORT": "5432"}):
            test_settings = Settings()
            assert isinstance(test_settings.POSTGRES_PORT, int)
            assert test_settings.POSTGRES_PORT == 5432

    def test_settings_with_missing_redis_env_vars(self):
        """Test settings initialization with missing Redis environment variables."""
        env_without_redis = {k: v for k, v in os.environ.items() 
                           if not k.startswith('REDIS_')}
        
        with patch.dict(os.environ, env_without_redis, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            error_details = exc_info.value.errors()
            redis_fields = ['REDIS_HOST', 'REDIS_DOCKER_PORT', 'REDIS_STREAM_NAME', 
                          'REDIS_CONSUMER_GROUP', 'REDIS_CONSUMER_NAME', 
                          'REDIS_BIKE_STATE_HASH', 'REDIS_STATION_BIKES_SET_PREFIX']
            
            missing_fields = [error['loc'][0] for error in error_details]
            for field in redis_fields:
                assert field in missing_fields

    def test_settings_with_missing_postgres_env_vars(self):
        """Test settings initialization with missing PostgreSQL environment variables."""
        env_without_postgres = {k: v for k, v in os.environ.items() 
                              if not k.startswith('POSTGRES_')}
        
        with patch.dict(os.environ, env_without_postgres, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            error_details = exc_info.value.errors()
            postgres_fields = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_SERVER', 
                             'POSTGRES_PORT', 'POSTGRES_DB']
            
            missing_fields = [error['loc'][0] for error in error_details]
            for field in postgres_fields:
                assert field in missing_fields

    def test_settings_with_invalid_port_values(self):
        """Test settings with invalid port values."""
        with patch.dict(os.environ, {"REDIS_DOCKER_PORT": "invalid_port"}):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            error_details = exc_info.value.errors()
            port_errors = [error for error in error_details 
                         if error['loc'][0] == 'REDIS_DOCKER_PORT']
            assert len(port_errors) > 0
            assert 'int_parsing' in port_errors[0]['type']

        with patch.dict(os.environ, {"POSTGRES_PORT": "not_a_number"}):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            error_details = exc_info.value.errors()
            port_errors = [error for error in error_details 
                         if error['loc'][0] == 'POSTGRES_PORT']
            assert len(port_errors) > 0
            assert 'int_parsing' in port_errors[0]['type']

    def test_settings_with_negative_port_values(self):
        """Test settings with negative port values."""
        with patch.dict(os.environ, {"REDIS_DOCKER_PORT": "-1"}):
            test_settings = Settings()
            assert test_settings.REDIS_DOCKER_PORT == -1  # Pydantic allows negative integers

        with patch.dict(os.environ, {"POSTGRES_PORT": "-5432"}):
            test_settings = Settings()
            assert test_settings.POSTGRES_PORT == -5432

    def test_settings_with_very_large_port_values(self):
        """Test settings with very large port values."""
        with patch.dict(os.environ, {"REDIS_DOCKER_PORT": "99999"}):
            test_settings = Settings()
            assert test_settings.REDIS_DOCKER_PORT == 99999

        with patch.dict(os.environ, {"POSTGRES_PORT": "65535"}):
            test_settings = Settings()
            assert test_settings.POSTGRES_PORT == 65535

    def test_settings_with_zero_port_values(self):
        """Test settings with zero port values."""
        with patch.dict(os.environ, {"REDIS_DOCKER_PORT": "0"}):
            test_settings = Settings()
            assert test_settings.REDIS_DOCKER_PORT == 0

        with patch.dict(os.environ, {"POSTGRES_PORT": "0"}):
            test_settings = Settings()
            assert test_settings.POSTGRES_PORT == 0

    def test_settings_string_fields_with_empty_values(self):
        """Test settings with empty string values."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "",
            "REDIS_STREAM_NAME": "",
            "POSTGRES_USER": "",
            "POSTGRES_PASSWORD": "",
            "POSTGRES_DB": ""
        }):
            test_settings = Settings()
            assert test_settings.REDIS_HOST == ""
            assert test_settings.REDIS_STREAM_NAME == ""
            assert test_settings.POSTGRES_USER == ""
            assert test_settings.POSTGRES_PASSWORD == ""
            assert test_settings.POSTGRES_DB == ""

    def test_settings_string_fields_with_whitespace(self):
        """Test settings with whitespace-only values."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "   ",
            "REDIS_STREAM_NAME": "\t\n",
            "POSTGRES_SERVER": " localhost ",
            "POSTGRES_DB": "  test_db  "
        }):
            test_settings = Settings()
            assert test_settings.REDIS_HOST == "   "
            assert test_settings.REDIS_STREAM_NAME == "\t\n"
            assert test_settings.POSTGRES_SERVER == " localhost "
            assert test_settings.POSTGRES_DB == "  test_db  "

    def test_settings_with_very_long_string_values(self):
        """Test settings with very long string values."""
        long_string = "x" * 1000
        with patch.dict(os.environ, {
            "REDIS_HOST": long_string,
            "POSTGRES_SERVER": long_string,
            "POSTGRES_DB": long_string
        }):
            test_settings = Settings()
            assert test_settings.REDIS_HOST == long_string
            assert test_settings.POSTGRES_SERVER == long_string
            assert test_settings.POSTGRES_DB == long_string

    def test_database_url_with_empty_components(self):
        """Test database URL construction with empty components."""
        with patch.dict(os.environ, {
            "POSTGRES_USER": "",
            "POSTGRES_PASSWORD": "",
            "POSTGRES_SERVER": "",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": ""
        }):
            test_settings = Settings()
            expected_url = "postgresql://:@:5432/"
            assert test_settings.database_url == expected_url

    def test_global_settings_instance(self):
        """Test that the global settings instance is properly initialized."""
        assert settings is not None
        assert isinstance(settings, Settings)
        # Basic check that it has the expected attributes
        assert hasattr(settings, 'REDIS_HOST')
        assert hasattr(settings, 'POSTGRES_USER')
        assert hasattr(settings, 'database_url')

    def test_settings_model_config(self):
        """Test that model configuration is properly set."""
        test_settings = Settings()
        assert hasattr(test_settings, 'model_config')
        # In Pydantic v2, model_config is a dict
        assert test_settings.model_config['env_file'] == '.env'

    def test_settings_redis_fields_exist(self):
        """Test that all Redis-related fields exist."""
        # Test with an instance instead of the class
        test_settings = Settings()
        redis_fields = [
            'REDIS_HOST', 'REDIS_DOCKER_PORT', 'REDIS_STREAM_NAME',
            'REDIS_CONSUMER_GROUP', 'REDIS_CONSUMER_NAME',
            'REDIS_BIKE_STATE_HASH', 'REDIS_STATION_BIKES_SET_PREFIX'
        ]
        
        for field in redis_fields:
            assert hasattr(test_settings, field)

    def test_settings_postgres_fields_exist(self):
        """Test that all PostgreSQL-related fields exist."""
        # Test with an instance instead of the class
        test_settings = Settings()
        postgres_fields = [
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_SERVER',
            'POSTGRES_PORT', 'POSTGRES_DB'
        ]
        
        for field in postgres_fields:
            assert hasattr(test_settings, field)