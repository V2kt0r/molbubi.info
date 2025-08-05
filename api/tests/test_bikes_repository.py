import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Query
from app.bikes.repository import BikeRepository


class TestBikeRepository:
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        # Setup query chain for all tests
        query_mock = Mock()
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        query_mock.first.return_value = None
        query_mock.count.return_value = 0
        query_mock.distinct.return_value = query_mock
        query_mock.group_by.return_value = query_mock
        query_mock.subquery.return_value = Mock()
        
        db.query.return_value = query_mock
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return BikeRepository(mock_db)

    def test_init(self, mock_db):
        repo = BikeRepository(mock_db)
        assert repo.db == mock_db

    def test_get_movements_basic(self, repository, mock_db):
        result = repository.get_movements("BIKE123")
        
        # Verify database query was called
        mock_db.query.assert_called()
        query_mock = mock_db.query.return_value
        
        # Verify joins and filters were applied
        assert query_mock.join.call_count == 2  # Two station joins
        query_mock.filter.assert_called()
        query_mock.order_by.assert_called()
        query_mock.offset.assert_called_with(0)
        query_mock.limit.assert_called_with(25)
        query_mock.all.assert_called()

    def test_get_movements_with_pagination(self, repository, mock_db):
        repository.get_movements("BIKE123", skip=10, limit=50)
        
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(10)
        query_mock.limit.assert_called_with(50)

    def test_get_movements_with_days_back(self, repository, mock_db):
        repository.get_movements("BIKE123", days_back=7)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter call for date filtering
        assert query_mock.filter.call_count >= 2

    def test_get_movements_with_start_date(self, repository, mock_db):
        start_date = datetime(2023, 1, 1)
        repository.get_movements("BIKE123", start_date=start_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter call for start date
        assert query_mock.filter.call_count >= 2

    def test_get_movements_with_end_date(self, repository, mock_db):
        end_date = datetime(2023, 12, 31)
        repository.get_movements("BIKE123", end_date=end_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter calls
        assert query_mock.filter.call_count >= 2

    def test_get_movements_start_date_overrides_days_back(self, repository, mock_db):
        start_date = datetime(2023, 1, 1)
        repository.get_movements("BIKE123", days_back=30, start_date=start_date)
        
        # When start_date is provided, days_back should be ignored
        query_mock = mock_db.query.return_value
        assert query_mock.filter.call_count >= 2

    def test_get_latest_movement(self, repository, mock_db):
        result = repository.get_latest_movement("BIKE123")
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.order_by.assert_called()
        query_mock.first.assert_called()

    def test_get_latest_movement_with_days_back(self, repository, mock_db):
        repository.get_latest_movement("BIKE123", days_back=7)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter call for date filtering
        assert query_mock.filter.call_count >= 2

    def test_get_latest_movement_no_days_back(self, repository, mock_db):
        repository.get_latest_movement("BIKE123", days_back=None)
        
        query_mock = mock_db.query.return_value
        # Should only have one filter call (for bike_number)
        query_mock.filter.assert_called()

    def test_get_all_summary(self, repository, mock_db):
        result = repository.get_all_summary()
        
        # Should make multiple query calls for subqueries
        assert mock_db.query.call_count >= 1
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(0)
        query_mock.limit.assert_called_with(100)

    def test_get_all_summary_with_pagination(self, repository, mock_db):
        repository.get_all_summary(skip=20, limit=50)
        
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(20)
        query_mock.limit.assert_called_with(50)

    def test_count_movements_basic(self, repository, mock_db):
        result = repository.count_movements("BIKE123")
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.count.assert_called()

    def test_count_movements_with_start_date(self, repository, mock_db):
        start_date = datetime(2023, 1, 1)
        repository.count_movements("BIKE123", start_date=start_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter calls
        assert query_mock.filter.call_count >= 2

    def test_count_movements_with_end_date(self, repository, mock_db):
        end_date = datetime(2023, 12, 31)
        repository.count_movements("BIKE123", end_date=end_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter calls
        assert query_mock.filter.call_count >= 2

    def test_count_all_summary(self, repository, mock_db):
        result = repository.count_all_summary()
        
        query_mock = mock_db.query.return_value
        query_mock.distinct.assert_called()
        query_mock.count.assert_called()