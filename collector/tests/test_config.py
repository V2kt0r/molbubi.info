"""
Comprehensive tests for configuration management covering all edge cases.
"""
import os
import pytest
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from app.core.config import Settings


class TestSettings:
    """Test cases for Settings configuration class."""

    def test_settings_with_valid_env_vars(self):
        """Test settings loading with valid environment variables."""
        env_vars = {
            "API_URL": "https://test-api.example.com/data",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream_name"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.API_URL == "https://test-api.example.com/data"
            assert settings.POLLING_INTERVAL_SECONDS == 30
            assert settings.REDIS_HOST == "redis.example.com"
            assert settings.REDIS_DOCKER_PORT == 6380
            assert settings.REDIS_STREAM_NAME == "test_stream_name"

    def test_settings_missing_api_url(self):
        """Test settings validation fails when API_URL is missing."""
        env_vars = {
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("API_URL",) and error["type"] == "missing" for error in errors)

    def test_settings_missing_polling_interval(self):
        """Test settings validation fails when POLLING_INTERVAL_SECONDS is missing."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("POLLING_INTERVAL_SECONDS",) and error["type"] == "missing" for error in errors)

    def test_settings_missing_redis_host(self):
        """Test settings validation fails when REDIS_HOST is missing."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("REDIS_HOST",) and error["type"] == "missing" for error in errors)

    def test_settings_missing_redis_port(self):
        """Test settings validation fails when REDIS_DOCKER_PORT is missing."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("REDIS_DOCKER_PORT",) and error["type"] == "missing" for error in errors)

    def test_settings_missing_stream_name(self):
        """Test settings validation fails when REDIS_STREAM_NAME is missing."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("REDIS_STREAM_NAME",) and error["type"] == "missing" for error in errors)

    def test_settings_invalid_polling_interval_type(self):
        """Test settings validation fails with invalid polling interval type."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "not_an_integer",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("POLLING_INTERVAL_SECONDS",) and error["type"] == "int_parsing" for error in errors)

    def test_settings_invalid_redis_port_type(self):
        """Test settings validation fails with invalid Redis port type."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "not_an_integer",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("REDIS_DOCKER_PORT",) and error["type"] == "int_parsing" for error in errors)

    def test_settings_negative_polling_interval(self):
        """Test settings with negative polling interval."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "-10",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.POLLING_INTERVAL_SECONDS == -10  # Pydantic allows negative integers

    def test_settings_zero_polling_interval(self):
        """Test settings with zero polling interval."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "0",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.POLLING_INTERVAL_SECONDS == 0

    def test_settings_large_polling_interval(self):
        """Test settings with very large polling interval."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "999999",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.POLLING_INTERVAL_SECONDS == 999999

    def test_settings_invalid_redis_port_range(self):
        """Test settings with Redis port outside valid range."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "99999",  # Outside typical port range
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.REDIS_DOCKER_PORT == 99999  # Pydantic allows it

    def test_settings_zero_redis_port(self):
        """Test settings with zero Redis port."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "0",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.REDIS_DOCKER_PORT == 0

    def test_settings_empty_string_values(self):
        """Test settings with empty string values."""
        env_vars = {
            "API_URL": "",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": ""
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == ""
            assert settings.REDIS_HOST == ""
            assert settings.REDIS_STREAM_NAME == ""

    def test_settings_whitespace_string_values(self):
        """Test settings with whitespace string values."""
        env_vars = {
            "API_URL": "   https://test-api.example.com   ",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "  redis.example.com  ",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "  test_stream  "
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            # Pydantic doesn't automatically strip whitespace
            assert settings.API_URL == "   https://test-api.example.com   "
            assert settings.REDIS_HOST == "  redis.example.com  "
            assert settings.REDIS_STREAM_NAME == "  test_stream  "

    def test_settings_unicode_string_values(self):
        """Test settings with unicode string values."""
        env_vars = {
            "API_URL": "https://测试-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.例え.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "测试_stream_🚲"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == "https://测试-api.example.com"
            assert settings.REDIS_HOST == "redis.例え.com"
            assert settings.REDIS_STREAM_NAME == "测试_stream_🚲"

    def test_settings_special_characters(self):
        """Test settings with special characters."""
        env_vars = {
            "API_URL": "https://api.example.com/path?param=value&other=123",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis-cluster.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "stream:with:colons-and-dashes_and_underscores"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == "https://api.example.com/path?param=value&other=123"
            assert settings.REDIS_HOST == "redis-cluster.example.com"
            assert settings.REDIS_STREAM_NAME == "stream:with:colons-and-dashes_and_underscores"

    def test_settings_env_file_loading(self):
        """Test settings model config specifies env file."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            # Verify settings were loaded (env vars take precedence over .env file)
            assert settings.API_URL == "https://test-api.example.com"
            assert settings.POLLING_INTERVAL_SECONDS == 30
            assert settings.REDIS_HOST == "redis.example.com"
            assert settings.REDIS_DOCKER_PORT == 6380
            assert settings.REDIS_STREAM_NAME == "test_stream"

    def test_settings_env_vars_override_env_file(self):
        """Test that environment variables override .env file values."""
        env_file_content = """API_URL=https://env-file-api.example.com
POLLING_INTERVAL_SECONDS=60"""
        
        env_vars = {
            "API_URL": "https://env-var-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch("builtins.open", mock_open(read_data=env_file_content)):
            with patch("os.path.exists", return_value=True):
                with patch.dict(os.environ, env_vars):
                    settings = Settings()
                    
                    # Environment variables should override .env file
                    assert settings.API_URL == "https://env-var-api.example.com"
                    assert settings.POLLING_INTERVAL_SECONDS == 30

    def test_settings_case_sensitivity(self):
        """Test that settings are case sensitive."""
        env_vars = {
            "api_url": "https://lowercase-api.example.com",  # Wrong case
            "API_URL": "https://correct-api.example.com",   # Correct case
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == "https://correct-api.example.com"

    def test_settings_boolean_like_strings(self):
        """Test settings don't convert boolean-like strings for string fields."""
        env_vars = {
            "API_URL": "true",  # Should remain as string
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "false",  # Should remain as string
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "True"  # Should remain as string
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == "true"
            assert settings.REDIS_HOST == "false"
            assert settings.REDIS_STREAM_NAME == "True"

    def test_settings_numeric_strings_for_string_fields(self):
        """Test settings keep numeric strings as strings for string fields."""
        env_vars = {
            "API_URL": "12345",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "67890",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "999"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.API_URL == "12345"
            assert settings.REDIS_HOST == "67890"
            assert settings.REDIS_STREAM_NAME == "999"
            assert isinstance(settings.API_URL, str)
            assert isinstance(settings.REDIS_HOST, str)
            assert isinstance(settings.REDIS_STREAM_NAME, str)

    def test_settings_model_config(self):
        """Test that model configuration is set correctly."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            # Verify that the model config includes env_file
            assert hasattr(settings, 'model_config')
            assert settings.model_config['env_file'] == '.env'

    def test_settings_multiple_instantiation(self):
        """Test that multiple Settings instances work correctly."""
        env_vars = {
            "API_URL": "https://test-api.example.com",
            "POLLING_INTERVAL_SECONDS": "30",
            "REDIS_HOST": "redis.example.com",
            "REDIS_DOCKER_PORT": "6380",
            "REDIS_STREAM_NAME": "test_stream"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings1 = Settings()
            settings2 = Settings()
            
            # Both instances should have same values
            assert settings1.API_URL == settings2.API_URL
            assert settings1.POLLING_INTERVAL_SECONDS == settings2.POLLING_INTERVAL_SECONDS
            assert settings1.REDIS_HOST == settings2.REDIS_HOST
            assert settings1.REDIS_DOCKER_PORT == settings2.REDIS_DOCKER_PORT
            assert settings1.REDIS_STREAM_NAME == settings2.REDIS_STREAM_NAME
            
            # But they should be different instances
            assert settings1 is not settings2