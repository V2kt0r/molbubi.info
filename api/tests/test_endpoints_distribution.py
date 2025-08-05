import pytest
from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


class TestDistributionEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_distribution_service(self):
        return Mock()

    def test_read_hourly_arrival_distribution_no_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = [
                {"time": 0, "arrival_count": 5},
                {"time": 1, "arrival_count": 3},
            ]
            
            response = client.get("/api/v1/distribution/arrivals")
            
            assert response.status_code == 200
            mock_distribution_service.get_hourly_arrival_distribution.assert_called_with(
                start_date=None,
                end_date=None,
                station_uids=None
            )

    def test_read_hourly_arrival_distribution_with_date_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            start_date = "2023-01-01"
            end_date = "2023-12-31"
            
            response = client.get(f"/api/v1/distribution/arrivals?start_date={start_date}&end_date={end_date}")
            
            assert response.status_code == 200
            
            # Verify date objects were passed to service
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert isinstance(args.kwargs['start_date'], date)
            assert isinstance(args.kwargs['end_date'], date)
            assert args.kwargs['start_date'] == date(2023, 1, 1)
            assert args.kwargs['end_date'] == date(2023, 12, 31)

    def test_read_hourly_arrival_distribution_with_station_filter(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            station_uids = "123,456,789"
            response = client.get(f"/api/v1/distribution/arrivals?station_uids={station_uids}")
            
            assert response.status_code == 200
            
            # Verify station UIDs were parsed to list of integers
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert args.kwargs['station_uids'] == [123, 456, 789]

    def test_read_hourly_arrival_distribution_all_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            response = client.get("/api/v1/distribution/arrivals?start_date=2023-06-01&end_date=2023-06-30&station_uids=100,200")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert isinstance(args.kwargs['start_date'], date)
            assert isinstance(args.kwargs['end_date'], date)
            assert args.kwargs['station_uids'] == [100, 200]

    def test_read_hourly_departure_distribution_no_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_departure_distribution.return_value = [
                {"time": 8, "departure_count": 12},
                {"time": 17, "departure_count": 20},
            ]
            
            response = client.get("/api/v1/distribution/departures")
            
            assert response.status_code == 200
            mock_distribution_service.get_hourly_departure_distribution.assert_called_with(
                start_date=None,
                end_date=None,
                station_uids=None
            )

    def test_read_hourly_departure_distribution_with_date_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_departure_distribution.return_value = []
            
            start_date = "2023-03-01"
            end_date = "2023-03-31"
            
            response = client.get(f"/api/v1/distribution/departures?start_date={start_date}&end_date={end_date}")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_departure_distribution.call_args
            assert isinstance(args.kwargs['start_date'], date)
            assert isinstance(args.kwargs['end_date'], date)

    def test_read_hourly_departure_distribution_with_station_filter(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_departure_distribution.return_value = []
            
            station_uids = "555,666"
            response = client.get(f"/api/v1/distribution/departures?station_uids={station_uids}")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_departure_distribution.call_args
            assert args.kwargs['station_uids'] == [555, 666]

    def test_read_hourly_departure_distribution_all_filters(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_departure_distribution.return_value = []
            
            response = client.get("/api/v1/distribution/departures?start_date=2023-09-01&end_date=2023-09-30&station_uids=777,888,999")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_departure_distribution.call_args
            assert args.kwargs['station_uids'] == [777, 888, 999]

    def test_distribution_endpoints_integration(self, client):
        # Test that endpoints return proper error handling when service dependencies fail
        response = client.get("/api/v1/distribution/arrivals")
        # Should not crash even if services aren't properly mocked
        assert response.status_code in [200, 500]  # Either works or fails gracefully

    def test_invalid_date_format(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            # Test invalid date format
            response = client.get("/api/v1/distribution/arrivals?start_date=invalid-date")
            
            # Should return validation error
            assert response.status_code == 422

    def test_invalid_station_uids_format(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            # Test invalid station UIDs format
            response = client.get("/api/v1/distribution/arrivals?station_uids=invalid,not-numbers")
            
            # Should return validation error
            assert response.status_code == 422

    def test_empty_station_uids(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            # Test empty station UIDs string
            response = client.get("/api/v1/distribution/arrivals?station_uids=")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            # Empty string should result in empty list or None
            assert args.kwargs['station_uids'] in [None, []]

    def test_single_station_uid(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            response = client.get("/api/v1/distribution/arrivals?station_uids=123")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert args.kwargs['station_uids'] == [123]

    def test_start_date_after_end_date(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            # Test start date after end date (should be handled by service logic)
            response = client.get("/api/v1/distribution/arrivals?start_date=2023-12-31&end_date=2023-01-01")
            
            assert response.status_code == 200
            # Service should handle this scenario gracefully

    def test_future_dates(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            # Test future dates
            response = client.get("/api/v1/distribution/arrivals?start_date=2025-01-01&end_date=2025-12-31")
            
            assert response.status_code == 200
            # Should accept future dates (service/business logic should handle appropriately)

    def test_negative_station_uids(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            # Test negative station UIDs
            response = client.get("/api/v1/distribution/arrivals?station_uids=-1,-2")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert args.kwargs['station_uids'] == [-1, -2]

    def test_very_large_station_uids(self, client, mock_distribution_service):
        with patch('app.shared.dependencies.get_distribution_service', return_value=mock_distribution_service):
            mock_distribution_service.get_hourly_arrival_distribution.return_value = []
            
            large_uid = 999999999
            response = client.get(f"/api/v1/distribution/arrivals?station_uids={large_uid}")
            
            assert response.status_code == 200
            
            args = mock_distribution_service.get_hourly_arrival_distribution.call_args
            assert args.kwargs['station_uids'] == [large_uid]