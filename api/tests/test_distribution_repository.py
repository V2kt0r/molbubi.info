import pytest
from datetime import date
from unittest.mock import Mock
from sqlalchemy.orm import Query
from app.distribution.repository import DistributionRepository


class TestDistributionRepository:
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.group_by.return_value = query_mock
        query_mock.all.return_value = []
        
        db.query.return_value = query_mock
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return DistributionRepository(mock_db)

    def test_init(self, mock_db):
        repo = DistributionRepository(mock_db)
        assert repo.db == mock_db

    def test_get_hourly_arrival_distribution_no_filters(self, repository, mock_db):
        # Mock empty results
        mock_db.query.return_value.all.return_value = []
        
        result = repository.get_hourly_arrival_distribution()
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.group_by.assert_called()
        query_mock.all.assert_called()
        
        # Should return 24 hours with 0 counts
        assert len(result) == 24
        assert all(item['arrival_count'] == 0 for item in result)
        assert [item['time'] for item in result] == list(range(24))

    def test_get_hourly_arrival_distribution_with_data(self, repository, mock_db):
        # Mock some data
        mock_db.query.return_value.all.return_value = [(8, 5), (12, 10), (18, 15)]
        
        result = repository.get_hourly_arrival_distribution()
        
        assert len(result) == 24
        assert result[8]['arrival_count'] == 5
        assert result[12]['arrival_count'] == 10
        assert result[18]['arrival_count'] == 15
        assert result[0]['arrival_count'] == 0  # Missing hour should be 0

    def test_get_hourly_arrival_distribution_with_date_filters(self, repository, mock_db):
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        
        repository.get_hourly_arrival_distribution(start_date=start_date, end_date=end_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter calls for date range
        assert query_mock.filter.call_count >= 3

    def test_get_hourly_arrival_distribution_with_station_filter(self, repository, mock_db):
        station_uids = [123, 456, 789]
        
        repository.get_hourly_arrival_distribution(station_uids=station_uids)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter call for stations
        assert query_mock.filter.call_count >= 2

    def test_get_hourly_arrival_distribution_all_filters(self, repository, mock_db):
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        station_uids = [123, 456]
        
        repository.get_hourly_arrival_distribution(
            start_date=start_date, 
            end_date=end_date, 
            station_uids=station_uids
        )
        
        query_mock = mock_db.query.return_value
        # Should have filter calls for base filters + date filters + station filter
        assert query_mock.filter.call_count >= 4

    def test_get_hourly_departure_distribution_no_filters(self, repository, mock_db):
        mock_db.query.return_value.all.return_value = []
        
        result = repository.get_hourly_departure_distribution()
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.group_by.assert_called()
        query_mock.all.assert_called()
        
        # Should return 24 hours with 0 counts
        assert len(result) == 24
        assert all(item['departure_count'] == 0 for item in result)
        assert [item['time'] for item in result] == list(range(24))

    def test_get_hourly_departure_distribution_with_data(self, repository, mock_db):
        # Mock some data
        mock_db.query.return_value.all.return_value = [(9, 3), (17, 8), (21, 12)]
        
        result = repository.get_hourly_departure_distribution()
        
        assert len(result) == 24
        assert result[9]['departure_count'] == 3
        assert result[17]['departure_count'] == 8
        assert result[21]['departure_count'] == 12
        assert result[1]['departure_count'] == 0  # Missing hour should be 0

    def test_get_hourly_departure_distribution_with_date_filters(self, repository, mock_db):
        start_date = date(2023, 6, 1)
        end_date = date(2023, 6, 30)
        
        repository.get_hourly_departure_distribution(start_date=start_date, end_date=end_date)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter calls for date range
        assert query_mock.filter.call_count >= 3

    def test_get_hourly_departure_distribution_with_station_filter(self, repository, mock_db):
        station_uids = [100, 200]
        
        repository.get_hourly_departure_distribution(station_uids=station_uids)
        
        query_mock = mock_db.query.return_value
        # Should have additional filter call for stations
        assert query_mock.filter.call_count >= 2

    def test_get_hourly_departure_distribution_all_filters(self, repository, mock_db):
        start_date = date(2023, 3, 1)
        end_date = date(2023, 3, 31)
        station_uids = [333, 444, 555]
        
        repository.get_hourly_departure_distribution(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )
        
        query_mock = mock_db.query.return_value
        # Should have filter calls for base filters + date filters + station filter
        assert query_mock.filter.call_count >= 4