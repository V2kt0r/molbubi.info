import os
import pytest
import time
import subprocess
import psycopg2
from unittest.mock import Mock, patch, call
from config import Settings
from run_migrations import main, wait_for_database, run_migrations


class TestEndToEndIntegration:
    """End-to-end integration tests for the complete migration process."""

    @pytest.mark.integration
    def test_complete_migration_process_success(self, mock_env_vars, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test complete successful migration process from start to finish."""
        # Setup mocks
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.\nINFO  [alembic.runtime.migration] Will assume transactional DDL.\nINFO  [alembic.runtime.migration] Running upgrade -> abc123, Create initial tables\nDone."
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Run the complete process
        main()
        
        # Verify database connection was established
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify migration was executed
        mock_subprocess_run.assert_called_once_with(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Should not have slept (database was ready immediately)
        mock_time_sleep.assert_not_called()

    @pytest.mark.integration
    def test_complete_migration_process_with_database_retry(self, mock_env_vars, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test complete migration process with database connection retries."""
        # Setup database connection to fail initially then succeed
        mock_conn = Mock()
        mock_psycopg2_connect.side_effect = [
            psycopg2.OperationalError("Connection refused"),
            psycopg2.OperationalError("Still refusing"),
            mock_conn  # Success on third attempt
        ]
        
        # Setup successful migration
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Migrations completed successfully"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Run the complete process
        main()
        
        # Verify database connection retries
        assert mock_psycopg2_connect.call_count == 3
        mock_conn.close.assert_called_once()
        
        # Verify sleep was called for retries
        assert mock_time_sleep.call_count == 2
        mock_time_sleep.assert_has_calls([call(2), call(2)])
        
        # Verify migration was eventually executed
        mock_subprocess_run.assert_called_once()

    @pytest.mark.integration 
    def test_migration_failure_after_database_ready(self, mock_env_vars, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test migration failure after database becomes ready."""
        # Setup successful database connection
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        # Setup migration failure
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["alembic", "upgrade", "head"]
        )
        error.stdout = "INFO  [alembic.runtime.migration] Context impl PostgresqlImpl."
        error.stderr = "ERROR: relation 'stations' already exists"
        mock_subprocess_run.side_effect = error
        
        # Run the process and expect it to exit with error
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        
        # Verify database connection was successful
        mock_psycopg2_connect.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify migration was attempted
        mock_subprocess_run.assert_called_once()

    @pytest.mark.integration
    def test_database_timeout_prevents_migration(self, mock_env_vars, mock_psycopg2_connect, mock_subprocess_run, mock_time_sleep):
        """Test that database timeout prevents migration from running."""
        # Setup database connection to always fail
        mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Database unavailable")
        
        # Run the process and expect it to exit with error
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        
        # Verify database connection was attempted multiple times (default 30)
        assert mock_psycopg2_connect.call_count == 30
        
        # Verify migration was never attempted
        mock_subprocess_run.assert_not_called()

    @pytest.mark.integration
    def test_configuration_and_execution_integration(self, mock_env_vars):
        """Test that configuration is properly loaded and used throughout execution."""
        expected_database_url = "postgresql://test_user:test_password@test_server:5432/test_db"
        
        with patch('psycopg2.connect') as mock_connect:
            with patch('subprocess.run') as mock_run:
                # Setup successful flow
                mock_conn = Mock()
                mock_connect.return_value = mock_conn
                
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = "Success"
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                
                # Run main process
                main()
                
                # Verify psycopg2.connect was called with the correct database URL
                mock_connect.assert_called_once_with(expected_database_url)
                
                # Verify subprocess.run was called with correct alembic command
                mock_run.assert_called_once_with(
                    ["alembic", "upgrade", "head"],
                    check=True,
                    capture_output=True,
                    text=True
                )


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    @pytest.mark.unit
    def test_invalid_environment_configuration(self):
        """Test handling of invalid environment configuration."""
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):  # ValidationError from pydantic
                from config import Settings
                Settings()

    @pytest.mark.unit
    def test_database_connection_permission_error(self, mock_env_vars, mock_time_sleep):
        """Test handling of database permission errors."""
        with patch('psycopg2.connect') as mock_connect:
            # Simulate permission denied error
            mock_connect.side_effect = psycopg2.OperationalError(
                "FATAL: permission denied for database \"test_db\""
            )
            
            with pytest.raises(SystemExit) as exc_info:
                wait_for_database(max_retries=2, retry_interval=0.1)
            
            assert exc_info.value.code == 1
            assert mock_connect.call_count == 2

    @pytest.mark.unit
    def test_alembic_command_not_found(self, mock_psycopg2_connect, mock_time_sleep):
        """Test handling when alembic command is not found."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate command not found
            mock_run.side_effect = FileNotFoundError("alembic: command not found")
            
            with pytest.raises(FileNotFoundError):
                run_migrations()

    @pytest.mark.unit
    def test_alembic_migration_syntax_error(self, mock_psycopg2_connect, mock_time_sleep):
        """Test handling of Alembic migration syntax errors."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate syntax error in migration
            error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["alembic", "upgrade", "head"]
            )
            error.stdout = ""
            error.stderr = "  File \"alembic/versions/abc123_create_tables.py\", line 15\n    def upgrade():\n                 ^\nIndentationError: expected an indented block"
            mock_run.side_effect = error
            
            with pytest.raises(SystemExit) as exc_info:
                run_migrations()
            
            assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_database_connection_interrupted(self, mock_env_vars):
        """Test handling of interrupted database connections."""
        with patch('psycopg2.connect') as mock_connect:
            with patch('time.sleep') as mock_sleep:
                # Simulate interrupted system call
                mock_connect.side_effect = [
                    psycopg2.OperationalError("Interrupted system call"),
                    psycopg2.OperationalError("Connection reset by peer"),
                    Mock()  # Success on third attempt
                ]
                
                wait_for_database(max_retries=5, retry_interval=0.1)
                
                assert mock_connect.call_count == 3
                assert mock_sleep.call_count == 2

    @pytest.mark.unit
    def test_migration_timeout_scenario(self, mock_psycopg2_connect):
        """Test scenario where migration process hangs/times out."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate a hanging process that gets killed
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["alembic", "upgrade", "head"],
                timeout=300
            )
            
            with pytest.raises(subprocess.TimeoutExpired):
                run_migrations()

    @pytest.mark.unit
    def test_partial_migration_failure(self, mock_psycopg2_connect):
        """Test handling of partial migration failures."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate partial migration failure
            error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["alembic", "upgrade", "head"]
            )
            error.stdout = "INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Add new column\nINFO  [alembic.runtime.migration] Running upgrade def456 -> ghi789, Add index"
            error.stderr = "sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateColumn) column \"new_column\" of relation \"stations\" already exists"
            mock_run.side_effect = error
            
            with pytest.raises(SystemExit) as exc_info:
                run_migrations()
            
            assert exc_info.value.code == 1


class TestConcurrencyScenarios:
    """Test scenarios involving concurrent migration attempts."""

    @pytest.mark.integration
    def test_concurrent_migration_detection(self, mock_psycopg2_connect):
        """Test detection of concurrent migration processes."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate migration lock conflict
            error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["alembic", "upgrade", "head"]
            )
            error.stdout = ""
            error.stderr = "DETAIL: Key (version_num)=(abc123) already exists."
            mock_run.side_effect = error
            
            with pytest.raises(SystemExit) as exc_info:
                run_migrations()
            
            assert exc_info.value.code == 1

    @pytest.mark.integration
    def test_database_lock_timeout(self, mock_psycopg2_connect):
        """Test handling of database lock timeouts during migration."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate lock timeout
            error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["alembic", "upgrade", "head"]
            )
            error.stdout = ""
            error.stderr = "ERROR: canceling statement due to lock timeout"
            mock_run.side_effect = error
            
            with pytest.raises(SystemExit) as exc_info:
                run_migrations()
            
            assert exc_info.value.code == 1


class TestResourceCleanup:
    """Test proper resource cleanup in various scenarios."""

    @pytest.mark.unit
    def test_database_connection_cleanup_on_success(self, mock_env_vars):
        """Test that database connections are properly closed on success."""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            wait_for_database(max_retries=1)
            
            mock_conn.close.assert_called_once()

    @pytest.mark.unit
    def test_database_connection_cleanup_on_failure(self, mock_env_vars):
        """Test that database connections are properly closed on failure."""
        with patch('psycopg2.connect') as mock_connect:
            with patch('time.sleep'):
                # All calls fail
                mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
                
                with pytest.raises(SystemExit):
                    wait_for_database(max_retries=2, retry_interval=0.1)
                
                # Should have attempted 2 connections
                assert mock_connect.call_count == 2

    @pytest.mark.unit
    def test_no_connection_leak_on_exception(self, mock_env_vars):
        """Test that connections don't leak when exceptions occur."""
        connections_created = []
        
        def mock_connect_side_effect(*args, **kwargs):
            mock_conn = Mock()
            connections_created.append(mock_conn)
            # First call succeeds, subsequent calls fail
            if len(connections_created) == 1:
                return mock_conn
            else:
                raise psycopg2.OperationalError("Connection failed")
        
        with patch('psycopg2.connect', side_effect=mock_connect_side_effect):
            with patch('time.sleep'):
                # This should succeed on first attempt
                wait_for_database(max_retries=3, retry_interval=0.1)
                
                # The successful connection should have been closed
                assert len(connections_created) == 1
                connections_created[0].close.assert_called_once()


class TestPerformanceScenarios:
    """Test performance-related scenarios and optimizations."""

    @pytest.mark.slow
    def test_rapid_retry_behavior(self, mock_env_vars):
        """Test behavior with very rapid retry attempts."""
        with patch('psycopg2.connect') as mock_connect:
            with patch('time.sleep') as mock_sleep:
                mock_connect.side_effect = psycopg2.OperationalError("Always fail")
                
                start_time = time.time()
                
                with pytest.raises(SystemExit):
                    wait_for_database(max_retries=10, retry_interval=0.01)
                
                end_time = time.time()
                
                # Should have completed quickly due to small retry interval
                assert end_time - start_time < 1.0  # Less than 1 second total
                assert mock_connect.call_count == 10
                assert mock_sleep.call_count == 10

    @pytest.mark.slow
    def test_long_running_migration_simulation(self, mock_psycopg2_connect):
        """Test handling of long-running migrations."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        with patch('subprocess.run') as mock_run:
            # Simulate long-running but successful migration
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "INFO  [alembic.runtime.migration] Running upgrade -> abc123, Large data migration\n" * 100 + "Done!"
            mock_result.stderr = ""
            
            def slow_run(*args, **kwargs):
                time.sleep(0.1)  # Simulate some processing time
                return mock_result
            
            mock_run.side_effect = slow_run
            
            start_time = time.time()
            run_migrations()
            end_time = time.time()
            
            # Should have taken some time but completed successfully
            assert end_time - start_time >= 0.1
            mock_run.assert_called_once()


class TestLogOutputScenarios:
    """Test various logging and output scenarios."""

    @pytest.mark.unit
    def test_migration_with_verbose_output(self, mock_psycopg2_connect, mock_subprocess_run):
        """Test migration with verbose Alembic output."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        # Simulate verbose migration output
        verbose_output = """INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Create stations table
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Create bike_movements table
INFO  [alembic.runtime.migration] Running upgrade def456 -> ghi789, Create bike_stays table
INFO  [alembic.runtime.migration] Running upgrade ghi789 -> jkl012, Add indexes"""
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = verbose_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Should handle verbose output without issues
        run_migrations()
        
        mock_subprocess_run.assert_called_once()

    @pytest.mark.unit
    def test_migration_with_warning_output(self, mock_psycopg2_connect, mock_subprocess_run):
        """Test migration with warning messages in output."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        # Simulate migration with warnings but success
        warning_output = """INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
WARNING [alembic.runtime.migration] Skipping index creation - already exists
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Create tables
WARNING [alembic.runtime.migration] Table 'stations' already has some data
Done."""
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = warning_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Should handle warnings without failing
        run_migrations()
        
        mock_subprocess_run.assert_called_once()

    @pytest.mark.unit
    def test_migration_with_mixed_output_streams(self, mock_psycopg2_connect, mock_subprocess_run):
        """Test migration with output in both stdout and stderr."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        # Simulate output in both streams (some tools use stderr for non-error output)
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "INFO  [alembic.runtime.migration] Migration completed"
        mock_result.stderr = "DEBUG: Connection established to database"
        mock_subprocess_run.return_value = mock_result
        
        # Should handle mixed output streams successfully
        run_migrations()
        
        mock_subprocess_run.assert_called_once()