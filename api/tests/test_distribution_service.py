import pytest
from datetime import date
from unittest.mock import Mock
from app.distribution.service import DistributionService


class TestDistributionService:
    @pytest.fixture
    def mock_distribution_repo(self):
        repo = Mock()
        repo.get_hourly_arrival_distribution.return_value = []
        repo.get_hourly_departure_distribution.return_value = []
        return repo

    @pytest.fixture
    def service(self, mock_distribution_repo):
        return DistributionService(mock_distribution_repo)

    def test_init(self, mock_distribution_repo):
        service = DistributionService(mock_distribution_repo)
        assert service.distribution_repo == mock_distribution_repo

    def test_get_hourly_arrival_distribution_no_filters(self, service, mock_distribution_repo):
        # Mock repository returns raw data
        mock_distribution_repo.get_hourly_arrival_distribution.return_value = [
            {'time': 0, 'arrival_count': 5},
            {'time': 1, 'arrival_count': 3},
            {'time': 23, 'arrival_count': 8}
        ]
        
        result = service.get_hourly_arrival_distribution()
        
        mock_distribution_repo.get_hourly_arrival_distribution.assert_called_with(
            start_date=None,
            end_date=None,
            station_uids=None
        )
        
        assert len(result) == 3
        assert result[0].time == 0
        assert result[0].arrival_count == 5
        assert result[1].time == 1
        assert result[1].arrival_count == 3
        assert result[2].time == 23
        assert result[2].arrival_count == 8

    def test_get_hourly_arrival_distribution_with_date_filters(self, service, mock_distribution_repo):
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        
        mock_distribution_repo.get_hourly_arrival_distribution.return_value = []
        
        service.get_hourly_arrival_distribution(start_date=start_date, end_date=end_date)
        
        mock_distribution_repo.get_hourly_arrival_distribution.assert_called_with(
            start_date=start_date,
            end_date=end_date,
            station_uids=None
        )

    def test_get_hourly_arrival_distribution_with_station_filter(self, service, mock_distribution_repo):
        station_uids = [123, 456, 789]
        
        mock_distribution_repo.get_hourly_arrival_distribution.return_value = []
        
        service.get_hourly_arrival_distribution(station_uids=station_uids)
        
        mock_distribution_repo.get_hourly_arrival_distribution.assert_called_with(
            start_date=None,
            end_date=None,
            station_uids=station_uids
        )

    def test_get_hourly_arrival_distribution_all_filters(self, service, mock_distribution_repo):
        start_date = date(2023, 6, 1)
        end_date = date(2023, 6, 30)
        station_uids = [100, 200]
        
        mock_distribution_repo.get_hourly_arrival_distribution.return_value = []
        
        service.get_hourly_arrival_distribution(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )
        
        mock_distribution_repo.get_hourly_arrival_distribution.assert_called_with(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )

    def test_get_hourly_arrival_distribution_empty_result(self, service, mock_distribution_repo):
        mock_distribution_repo.get_hourly_arrival_distribution.return_value = []
        
        result = service.get_hourly_arrival_distribution()
        
        assert result == []

    def test_get_hourly_departure_distribution_no_filters(self, service, mock_distribution_repo):
        # Mock repository returns raw data
        mock_distribution_repo.get_hourly_departure_distribution.return_value = [
            {'time': 6, 'departure_count': 12},
            {'time': 12, 'departure_count': 20},
            {'time': 18, 'departure_count': 15}
        ]
        
        result = service.get_hourly_departure_distribution()
        
        mock_distribution_repo.get_hourly_departure_distribution.assert_called_with(
            start_date=None,
            end_date=None,
            station_uids=None
        )
        
        assert len(result) == 3
        assert result[0].time == 6
        assert result[0].departure_count == 12
        assert result[1].time == 12
        assert result[1].departure_count == 20
        assert result[2].time == 18
        assert result[2].departure_count == 15

    def test_get_hourly_departure_distribution_with_date_filters(self, service, mock_distribution_repo):
        start_date = date(2023, 3, 1)
        end_date = date(2023, 3, 31)
        
        mock_distribution_repo.get_hourly_departure_distribution.return_value = []
        
        service.get_hourly_departure_distribution(start_date=start_date, end_date=end_date)
        
        mock_distribution_repo.get_hourly_departure_distribution.assert_called_with(
            start_date=start_date,
            end_date=end_date,
            station_uids=None
        )

    def test_get_hourly_departure_distribution_with_station_filter(self, service, mock_distribution_repo):
        station_uids = [555, 666]
        
        mock_distribution_repo.get_hourly_departure_distribution.return_value = []
        
        service.get_hourly_departure_distribution(station_uids=station_uids)
        
        mock_distribution_repo.get_hourly_departure_distribution.assert_called_with(
            start_date=None,
            end_date=None,
            station_uids=station_uids
        )

    def test_get_hourly_departure_distribution_all_filters(self, service, mock_distribution_repo):
        start_date = date(2023, 9, 1)
        end_date = date(2023, 9, 30)
        station_uids = [777, 888, 999]
        
        mock_distribution_repo.get_hourly_departure_distribution.return_value = []
        
        service.get_hourly_departure_distribution(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )
        
        mock_distribution_repo.get_hourly_departure_distribution.assert_called_with(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )

    def test_get_hourly_departure_distribution_empty_result(self, service, mock_distribution_repo):
        mock_distribution_repo.get_hourly_departure_distribution.return_value = []
        
        result = service.get_hourly_departure_distribution()
        
        assert result == []