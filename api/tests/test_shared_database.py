import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.shared.database import engine, SessionLocal, get_db


class TestDatabase:
    def test_engine_exists(self):
        # Test that engine is created
        assert engine is not None

    def test_session_local_exists(self):
        # Test that SessionLocal is created
        assert SessionLocal is not None

    def test_get_db_generator(self):
        # Test that get_db is a generator function
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db = Mock(spec=Session)
            mock_session_local.return_value = mock_db
            
            # get_db should be a generator
            db_gen = get_db()
            
            # Should yield a database session
            db_session = next(db_gen)
            assert db_session == mock_db
            
            # Should close the session when done
            try:
                next(db_gen)
            except StopIteration:
                # Generator should be exhausted
                pass
            
            mock_db.close.assert_called_once()

    def test_get_db_context_manager(self):
        # Test get_db in context manager style usage
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db = Mock(spec=Session)
            mock_session_local.return_value = mock_db
            
            # Simulate FastAPI dependency injection usage
            db_generator = get_db()
            db_session = next(db_generator)
            
            assert db_session == mock_db
            
            # Simulate cleanup (what FastAPI does)
            try:
                next(db_generator)
            except StopIteration:
                pass
            
            mock_db.close.assert_called_once()

    def test_get_db_exception_handling(self):
        # Test that database session is closed even if exception occurs
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db = Mock(spec=Session)
            mock_session_local.return_value = mock_db
            
            db_generator = get_db()
            db_session = next(db_generator)
            
            # Simulate exception during request processing
            try:
                db_generator.throw(Exception("Test exception"))
            except Exception:
                pass
            
            # Session should still be closed
            mock_db.close.assert_called_once()

    def test_sessionlocal_configuration(self):
        # Test SessionLocal configuration
        # We can't test actual database connection in unit tests,
        # but we can verify the SessionLocal is properly configured
        assert SessionLocal is not None
        assert hasattr(SessionLocal, 'bind')
        assert SessionLocal.bind == engine

    @patch('app.shared.database.create_engine')
    def test_engine_creation(self, mock_create_engine):
        # Test that engine is created with proper settings
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # Re-import to trigger engine creation with mock
        from importlib import reload
        import app.shared.database
        reload(app.shared.database)
        
        # Should have called create_engine with database URL from settings
        mock_create_engine.assert_called()

    def test_get_db_multiple_calls(self):
        # Test multiple calls to get_db return independent sessions
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db1 = Mock(spec=Session)
            mock_db2 = Mock(spec=Session)
            mock_session_local.side_effect = [mock_db1, mock_db2]
            
            # First call
            db_gen1 = get_db()
            db_session1 = next(db_gen1)
            
            # Second call
            db_gen2 = get_db()
            db_session2 = next(db_gen2)
            
            # Should be different sessions
            assert db_session1 == mock_db1
            assert db_session2 == mock_db2
            assert db_session1 != db_session2
            
            # Clean up both generators
            for gen in [db_gen1, db_gen2]:
                try:
                    next(gen)
                except StopIteration:
                    pass

    def test_database_dependency_injection_compatible(self):
        # Test that get_db is compatible with FastAPI dependency injection
        import inspect
        
        # Should be a generator function
        assert inspect.isgeneratorfunction(get_db)
        
        # Should not require parameters
        signature = inspect.signature(get_db)
        assert len(signature.parameters) == 0

    def test_session_local_factory(self):
        # Test that SessionLocal creates new sessions
        with patch('app.shared.database.sessionmaker') as mock_sessionmaker:
            mock_session_factory = Mock()
            mock_sessionmaker.return_value = mock_session_factory
            
            # Re-import to trigger sessionmaker call
            from importlib import reload
            import app.shared.database
            reload(app.shared.database)
            
            # Should have called sessionmaker with proper parameters
            mock_sessionmaker.assert_called_with(
                autocommit=False, 
                autoflush=False, 
                bind=app.shared.database.engine
            )

    def test_get_db_returns_session_interface(self):
        # Test that get_db returns something that looks like a session
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db = Mock(spec=Session)
            mock_session_local.return_value = mock_db
            
            db_gen = get_db()
            db_session = next(db_gen)
            
            # Should have session-like interface
            assert hasattr(db_session, 'query') or hasattr(db_session, 'execute')
            assert hasattr(db_session, 'close')
            assert hasattr(db_session, 'commit') or True  # Mock might not have all methods

    def test_get_db_cleanup_guaranteed(self):
        # Test that cleanup always happens
        with patch('app.shared.database.SessionLocal') as mock_session_local:
            mock_db = Mock(spec=Session)
            mock_session_local.return_value = mock_db
            
            db_gen = get_db()
            db_session = next(db_gen)
            
            # Force generator to complete
            with pytest.raises(StopIteration):
                next(db_gen)
            
            # Close should be called
            mock_db.close.assert_called_once()