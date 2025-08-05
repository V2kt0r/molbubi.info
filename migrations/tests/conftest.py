import os
import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from config import Settings


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_password',
        'POSTGRES_SERVER': 'test_server',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'test_db'
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def test_settings(mock_env_vars):
    """Create a Settings instance with test environment variables."""
    return Settings()


@pytest.fixture
def mock_database_url():
    """Mock database URL for testing."""
    return "postgresql://test_user:test_password@test_server:5432/test_db"


@pytest.fixture
def mock_psycopg2_connect():
    """Mock psycopg2.connect for database connection tests."""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        yield mock_connect


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for migration command tests."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Migration completed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_time_sleep():
    """Mock time.sleep to speed up tests."""
    with patch('time.sleep') as mock_sleep:
        yield mock_sleep


@pytest.fixture
def in_memory_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture
def mock_alembic_context():
    """Mock alembic context for testing."""
    with patch('alembic.context') as mock_context:
        mock_context.is_offline_mode.return_value = False
        mock_context.config = Mock()
        mock_context.config.get_main_option.return_value = "postgresql://test:test@localhost/test"
        mock_context.config.get_section.return_value = {}
        mock_context.config.config_ini_section = "alembic"
        yield mock_context