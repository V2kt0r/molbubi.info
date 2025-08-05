import sys
import pytest
from unittest.mock import Mock, patch, call
import psycopg2
import subprocess
from run_migrations import wait_for_database, run_migrations, main


class TestWaitForDatabase:
    """Test the wait_for_database function."""

    @pytest.mark.unit
    def test_database_ready_immediately(self, mock_psycopg2_connect, mock_time_sleep):
        """Test successful database connection on first attempt."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        wait_for_database()
        
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_time_sleep.assert_not_called()

    @pytest.mark.unit
    def test_database_ready_after_retries(self, mock_psycopg2_connect, mock_time_sleep):
        """Test database connection succeeds after a few retries."""
        mock_conn = Mock()
        mock_psycopg2_connect.side_effect = [
            psycopg2.OperationalError("Connection failed"),
            psycopg2.OperationalError("Still failing"),
            mock_conn  # Success on third attempt
        ]
        
        wait_for_database(max_retries=5, retry_interval=1)
        
        assert mock_psycopg2_connect.call_count == 3
        mock_conn.close.assert_called_once()
        assert mock_time_sleep.call_count == 2
        mock_time_sleep.assert_has_calls([call(1), call(1)])

    @pytest.mark.unit
    def test_database_timeout_exits(self, mock_psycopg2_connect, mock_time_sleep):
        """Test that function exits when database doesn't become ready."""
        mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Always failing")
        
        with pytest.raises(SystemExit) as exc_info:
            wait_for_database(max_retries=3, retry_interval=1)
        
        assert exc_info.value.code == 1
        assert mock_psycopg2_connect.call_count == 3
        assert mock_time_sleep.call_count == 3

    @pytest.mark.unit
    def test_custom_retry_parameters(self, mock_psycopg2_connect, mock_time_sleep):
        """Test wait_for_database with custom retry parameters."""
        mock_conn = Mock()
        mock_psycopg2_connect.side_effect = [
            psycopg2.OperationalError("Fail"),
            mock_conn
        ]
        
        wait_for_database(max_retries=10, retry_interval=5)
        
        assert mock_psycopg2_connect.call_count == 2
        mock_conn.close.assert_called_once()
        mock_time_sleep.assert_called_once_with(5)

    @pytest.mark.unit
    def test_default_parameters(self, mock_psycopg2_connect, mock_time_sleep):
        """Test wait_for_database uses default parameters correctly."""
        mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Always failing")
        
        with pytest.raises(SystemExit):
            wait_for_database()  # Use defaults: max_retries=30, retry_interval=2
        
        assert mock_psycopg2_connect.call_count == 30
        assert mock_time_sleep.call_count == 30
        for call_args in mock_time_sleep.call_args_list:
            assert call_args[0][0] == 2  # retry_interval=2

    @pytest.mark.unit
    def test_connection_exception_handling(self, mock_time_sleep):
        """Test that only OperationalError is caught and other exceptions propagate."""
        with patch('psycopg2.connect') as mock_connect:
            mock_connect.side_effect = ValueError("Unexpected error")
            
            with pytest.raises(ValueError, match="Unexpected error"):
                wait_for_database(max_retries=1)

    @pytest.mark.unit
    def test_zero_retries(self, mock_psycopg2_connect):
        """Test behavior with zero retries."""
        mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Failed")
        
        with pytest.raises(SystemExit) as exc_info:
            wait_for_database(max_retries=0)
        
        assert exc_info.value.code == 1
        mock_psycopg2_connect.assert_not_called()


class TestRunMigrations:
    """Test the run_migrations function."""

    @pytest.mark.unit
    def test_successful_migration(self, mock_subprocess_run):
        """Test successful migration execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Running migrations...\nDone!"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        run_migrations()
        
        mock_subprocess_run.assert_called_once_with(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )

    @pytest.mark.unit
    def test_migration_with_empty_output(self, mock_subprocess_run):
        """Test migration with no stdout output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        run_migrations()
        
        mock_subprocess_run.assert_called_once()

    @pytest.mark.unit
    def test_migration_failure_with_stderr(self, mock_subprocess_run):
        """Test migration failure with stderr output."""
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["alembic", "upgrade", "head"]
        )
        error.stdout = "Some stdout"
        error.stderr = "Migration failed: table already exists"
        mock_subprocess_run.side_effect = error
        
        with pytest.raises(SystemExit) as exc_info:
            run_migrations()
        
        assert exc_info.value.code == 1
        mock_subprocess_run.assert_called_once()

    @pytest.mark.unit
    def test_migration_failure_without_output(self, mock_subprocess_run):
        """Test migration failure without output."""
        error = subprocess.CalledProcessError(
            returncode=2,
            cmd=["alembic", "upgrade", "head"]
        )
        error.stdout = ""
        error.stderr = ""
        mock_subprocess_run.side_effect = error
        
        with pytest.raises(SystemExit) as exc_info:
            run_migrations()
        
        assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_migration_failure_only_stdout(self, mock_subprocess_run):
        """Test migration failure with only stdout."""
        error = subprocess.CalledProcessError(
            returncode=3,
            cmd=["alembic", "upgrade", "head"]
        )
        error.stdout = "Error in stdout"
        error.stderr = ""
        mock_subprocess_run.side_effect = error
        
        with pytest.raises(SystemExit) as exc_info:
            run_migrations()
        
        assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_migration_unexpected_exception(self, mock_subprocess_run):
        """Test migration with unexpected exception."""
        mock_subprocess_run.side_effect = OSError("Unexpected OS error")
        
        with pytest.raises(OSError, match="Unexpected OS error"):
            run_migrations()


class TestMain:
    """Test the main function."""

    @pytest.mark.unit
    def test_main_successful_flow(self, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test complete successful migration flow."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Migration successful"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        main()
        
        # Verify database wait was called
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify migration was called
        mock_subprocess_run.assert_called_once_with(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )

    @pytest.mark.unit
    def test_main_database_timeout_exits(self, mock_psycopg2_connect, mock_time_sleep):
        """Test main exits when database timeout occurs."""
        mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Database unavailable")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_main_migration_failure_exits(self, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test main exits when migration fails."""
        # Database connection succeeds
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        # Migration fails
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["alembic", "upgrade", "head"]
        )
        error.stdout = ""
        error.stderr = "Migration error"
        mock_subprocess_run.side_effect = error
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        
        # Verify database connection was attempted
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()

    @pytest.mark.unit
    def test_main_with_database_retries(self, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test main with database connection retries."""
        mock_conn = Mock()
        mock_psycopg2_connect.side_effect = [
            psycopg2.OperationalError("Connection failed"),
            mock_conn
        ]
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        main()
        
        # Verify retry behavior
        assert mock_psycopg2_connect.call_count == 2
        mock_conn.close.assert_called_once()
        mock_time_sleep.assert_called_once_with(2)  # Default retry_interval
        
        # Verify migration was eventually called
        mock_subprocess_run.assert_called_once()


class TestIntegrationScenarios:
    """Integration test scenarios for the complete migration process."""

    @pytest.mark.integration
    def test_complete_migration_flow_with_config(self, mock_env_vars, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test complete flow including config loading."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All migrations applied successfully"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Import and run main to test the complete flow
        from run_migrations import main
        main()
        
        # Verify the complete flow
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_subprocess_run.assert_called_once_with(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )

    @pytest.mark.integration
    def test_real_world_error_scenarios(self, mock_env_vars):
        """Test real-world error scenarios without mocking."""
        # This test uses minimal mocking to test real error paths
        
        with patch('psycopg2.connect') as mock_connect:
            # Simulate real database connection error
            mock_connect.side_effect = psycopg2.OperationalError("FATAL: database does not exist")
            
            with patch('time.sleep'):  # Speed up the test
                with pytest.raises(SystemExit) as exc_info:
                    wait_for_database(max_retries=2, retry_interval=0.1)
                
                assert exc_info.value.code == 1
                assert mock_connect.call_count == 2