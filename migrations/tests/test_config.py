import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from config import Settings


class TestSettings:
    """Test the Settings configuration class."""

    @pytest.mark.unit
    def test_settings_creation_with_valid_env_vars(self, test_settings):
        """Test creating Settings with valid environment variables."""
        assert test_settings.POSTGRES_USER == "test_user"
        assert test_settings.POSTGRES_PASSWORD == "test_password"
        assert test_settings.POSTGRES_SERVER == "test_server"
        assert test_settings.POSTGRES_PORT == 5432
        assert test_settings.POSTGRES_DB == "test_db"

    @pytest.mark.unit
    def test_database_url_property(self, test_settings):
        """Test database_url property generation."""
        expected_url = "postgresql://test_user:test_password@test_server:5432/test_db"
        assert test_settings.database_url == expected_url

    @pytest.mark.unit
    def test_database_url_with_special_characters(self):
        """Test database_url with special characters in password."""
        env_vars = {
            'POSTGRES_USER': 'user@domain',
            'POSTGRES_PASSWORD': 'pass@word!',
            'POSTGRES_SERVER': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test-db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            expected_url = "postgresql://user@domain:pass@word!@localhost:5432/test-db"
            assert settings.database_url == expected_url

    @pytest.mark.unit
    def test_missing_required_env_var_postgres_user(self):
        """Test Settings creation fails when POSTGRES_USER is missing."""
        env_vars = {
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["type"] == "missing"
            assert "POSTGRES_USER" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_missing_required_env_var_postgres_password(self):
        """Test Settings creation fails when POSTGRES_PASSWORD is missing."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["type"] == "missing"
            assert "POSTGRES_PASSWORD" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_missing_required_env_var_postgres_server(self):
        """Test Settings creation fails when POSTGRES_SERVER is missing."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["type"] == "missing"
            assert "POSTGRES_SERVER" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_missing_required_env_var_postgres_port(self):
        """Test Settings creation fails when POSTGRES_PORT is missing."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["type"] == "missing"
            assert "POSTGRES_PORT" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_missing_required_env_var_postgres_db(self):
        """Test Settings creation fails when POSTGRES_DB is missing."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': '5432'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["type"] == "missing"
            assert "POSTGRES_DB" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_invalid_port_type(self):
        """Test Settings creation fails with invalid port type."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': 'invalid_port',
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert "POSTGRES_PORT" in str(errors[0]["loc"])

    @pytest.mark.unit
    def test_all_missing_env_vars(self):
        """Test Settings creation fails when all required env vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            assert len(errors) == 5  # All 5 required fields are missing
            
            missing_fields = [str(error["loc"]) for error in errors]
            assert "('POSTGRES_USER',)" in missing_fields
            assert "('POSTGRES_PASSWORD',)" in missing_fields
            assert "('POSTGRES_SERVER',)" in missing_fields
            assert "('POSTGRES_PORT',)" in missing_fields
            assert "('POSTGRES_DB',)" in missing_fields

    @pytest.mark.unit
    def test_extra_env_vars_ignored(self):
        """Test that extra environment variables are ignored."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db',
            'EXTRA_VAR': 'should_be_ignored',
            'ANOTHER_EXTRA': 'also_ignored'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            # Should not have extra attributes
            assert not hasattr(settings, 'EXTRA_VAR')
            assert not hasattr(settings, 'ANOTHER_EXTRA')
            
            # Should still have all required attributes
            assert settings.POSTGRES_USER == "test_user"
            assert settings.POSTGRES_PASSWORD == "test_password"
            assert settings.POSTGRES_SERVER == "test_server"
            assert settings.POSTGRES_PORT == 5432
            assert settings.POSTGRES_DB == "test_db"

    @pytest.mark.unit
    def test_port_as_string_converted_to_int(self):
        """Test that port string is properly converted to integer."""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_SERVER': 'test_server',
            'POSTGRES_PORT': '9999',  # String port
            'POSTGRES_DB': 'test_db'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert isinstance(settings.POSTGRES_PORT, int)
            assert settings.POSTGRES_PORT == 9999