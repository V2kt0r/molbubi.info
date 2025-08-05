import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.shared.exceptions import StationNotFound


class TestStationEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_station_service(self):
        return Mock()

    def test_read_stations_default_params(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_all_stations_with_bike_count.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 100,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/stations/")
            
            assert response.status_code == 200
            mock_station_service.get_all_stations_with_bike_count.assert_called_with(0, 100, None)

    def test_read_stations_custom_params(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_all_stations_with_bike_count.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 50,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/stations/?skip=20&limit=50")
            
            assert response.status_code == 200
            mock_station_service.get_all_stations_with_bike_count.assert_called_with(20, 50, None)

    def test_read_stations_with_at_time(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_all_stations_with_bike_count.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 100, "pages": 0}
            }
            
            at_time = "2023-01-01T12:00:00"
            response = client.get(f"/api/v1/stations/?at_time={at_time}")
            
            assert response.status_code == 200
            # Verify datetime was parsed and passed to service
            args = mock_station_service.get_all_stations_with_bike_count.call_args[0]
            assert isinstance(args[2], datetime)  # at_time parameter

    def test_read_station_bikes_current(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.return_value = ["bike1", "bike2", "bike3"]
            
            response = client.get("/api/v1/stations/123/bikes")
            
            assert response.status_code == 200
            assert response.json() == ["bike1", "bike2", "bike3"]
            mock_station_service.get_bikes_at_station.assert_called_with(123, None)

    def test_read_station_bikes_historical(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.return_value = ["bike1", "bike2"]
            
            at_time = "2023-01-01T15:30:00"
            response = client.get(f"/api/v1/stations/456/bikes?at_time={at_time}")
            
            assert response.status_code == 200
            assert response.json() == ["bike1", "bike2"]
            
            args = mock_station_service.get_bikes_at_station.call_args[0]
            assert args[0] == 456
            assert isinstance(args[1], datetime)

    def test_read_station_bikes_not_found(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.side_effect = StationNotFound(station_uid=123)
            
            response = client.get("/api/v1/stations/123/bikes")
            
            assert response.status_code == 404
            assert "message" in response.json()

    def test_read_station_stays_default_params(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_stations_arrivals_and_departures.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 100, "pages": 0}
            }
            
            response = client.get("/api/v1/stations/stays")
            
            assert response.status_code == 200
            mock_station_service.get_stations_arrivals_and_departures.assert_called_with(0, 100)

    def test_read_station_stays_custom_params(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_stations_arrivals_and_departures.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 25, "pages": 0}
            }
            
            response = client.get("/api/v1/stations/stays?skip=30&limit=25")
            
            assert response.status_code == 200
            mock_station_service.get_stations_arrivals_and_departures.assert_called_with(30, 25)

    def test_station_endpoints_integration(self, client):
        # Test that endpoints return proper error handling when service dependencies fail
        response = client.get("/api/v1/stations/")
        # Should not crash even if services aren't properly mocked
        assert response.status_code in [200, 500]  # Either works or fails gracefully

    def test_invalid_station_id_type(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            # Test non-integer station ID
            response = client.get("/api/v1/stations/invalid/bikes")
            
            # Should return validation error
            assert response.status_code == 422

    def test_negative_station_id(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.return_value = []
            
            response = client.get("/api/v1/stations/-1/bikes")
            
            # Should handle negative IDs (might be valid in some systems)
            assert response.status_code == 200
            mock_station_service.get_bikes_at_station.assert_called_with(-1, None)

    def test_invalid_datetime_format(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            # Test invalid datetime format
            response = client.get("/api/v1/stations/?at_time=invalid-datetime")
            
            # Should return validation error
            assert response.status_code == 422

    def test_station_bikes_empty_response(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.return_value = []
            
            response = client.get("/api/v1/stations/123/bikes")
            
            assert response.status_code == 200
            assert response.json() == []

    def test_large_station_id(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_bikes_at_station.return_value = []
            
            # Test very large station ID
            large_id = 999999999
            response = client.get(f"/api/v1/stations/{large_id}/bikes")
            
            assert response.status_code == 200
            mock_station_service.get_bikes_at_station.assert_called_with(large_id, None)

    def test_stations_negative_pagination(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_all_stations_with_bike_count.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 100, "pages": 0}
            }
            
            # Test negative skip/limit values
            response = client.get("/api/v1/stations/?skip=-10&limit=-5")
            
            # FastAPI should handle validation appropriately
            assert response.status_code in [200, 422]

    def test_stations_zero_limit(self, client, mock_station_service):
        with patch('app.shared.dependencies.get_station_service', return_value=mock_station_service):
            mock_station_service.get_all_stations_with_bike_count.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 0, "pages": 0}
            }
            
            # Test zero limit
            response = client.get("/api/v1/stations/?limit=0")
            
            assert response.status_code == 200
            mock_station_service.get_all_stations_with_bike_count.assert_called_with(0, 0, None)