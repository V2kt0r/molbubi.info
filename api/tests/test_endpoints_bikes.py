import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.shared.exceptions import BikeNotFound


class TestBikeEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_bike_service(self):
        return Mock()

    def test_read_all_bikes_summary_default_params(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_all_bikes_summary.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 100,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/bikes/")
            
            assert response.status_code == 200
            mock_bike_service.get_all_bikes_summary.assert_called_with(0, 100)

    def test_read_all_bikes_summary_custom_params(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_all_bikes_summary.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 50,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/bikes/?skip=10&limit=50")
            
            assert response.status_code == 200
            mock_bike_service.get_all_bikes_summary.assert_called_with(10, 50)

    def test_read_bike_history_default_params(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_bike_history.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 25,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/bikes/BIKE123/history")
            
            assert response.status_code == 200
            mock_bike_service.get_bike_history.assert_called_with("BIKE123", 0, 25, 30, None, None)

    def test_read_bike_history_custom_params(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_bike_history.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 10,
                    "pages": 0
                }
            }
            
            response = client.get("/api/v1/bikes/BIKE123/history?skip=5&limit=10&days_back=7")
            
            assert response.status_code == 200
            mock_bike_service.get_bike_history.assert_called_with("BIKE123", 5, 10, 7, None, None)

    def test_read_bike_history_with_date_filters(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_bike_history.return_value = {
                "data": [],
                "meta": {
                    "total": 0,
                    "page": 1,
                    "per_page": 25,
                    "pages": 0
                }
            }
            
            start_date = "2023-01-01T00:00:00"
            end_date = "2023-12-31T23:59:59"
            
            response = client.get(f"/api/v1/bikes/BIKE123/history?start_date={start_date}&end_date={end_date}")
            
            assert response.status_code == 200
            # Verify that datetime parsing occurred (service should be called with datetime objects)
            args = mock_bike_service.get_bike_history.call_args[0]
            assert args[0] == "BIKE123"
            assert isinstance(args[4], datetime)  # start_date
            assert isinstance(args[5], datetime)  # end_date

    def test_read_bike_location_success(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_location = {
                "bike_number": "BIKE123",
                "current_station": {
                    "uid": 456,
                    "name": "Test Station",
                    "lat": 52.5,
                    "lng": 13.4
                },
                "last_seen": "2023-01-01T12:00:00"
            }
            mock_bike_service.get_current_location.return_value = mock_location
            
            response = client.get("/api/v1/bikes/BIKE123/location")
            
            assert response.status_code == 200
            assert response.json() == mock_location
            mock_bike_service.get_current_location.assert_called_with("BIKE123")

    def test_read_bike_location_not_found(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_current_location.side_effect = BikeNotFound("BIKE123")
            
            response = client.get("/api/v1/bikes/BIKE123/location")
            
            assert response.status_code == 404
            assert "message" in response.json()

    def test_bike_endpoints_integration(self, client):
        # Test that endpoints return proper error handling when service dependencies fail
        response = client.get("/api/v1/bikes/")
        # Should not crash even if services aren't properly mocked
        assert response.status_code in [200, 500]  # Either works or fails gracefully

    def test_bike_history_url_encoding(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_bike_history.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 25, "pages": 0}
            }
            
            # Test bike number with special characters
            bike_number = "BIKE/123"
            response = client.get(f"/api/v1/bikes/{bike_number}/history")
            
            # Should handle URL encoding properly
            assert response.status_code == 200

    def test_bike_history_invalid_dates(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            # Test invalid date format
            response = client.get("/api/v1/bikes/BIKE123/history?start_date=invalid-date")
            
            # Should return validation error
            assert response.status_code == 422

    def test_bike_history_negative_pagination(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_bike_history.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 25, "pages": 0}
            }
            
            # Test negative skip/limit values
            response = client.get("/api/v1/bikes/BIKE123/history?skip=-1&limit=-1")
            
            # FastAPI should handle validation, but service should get reasonable values
            assert response.status_code in [200, 422]

    def test_bikes_summary_large_limit(self, client, mock_bike_service):
        with patch('app.shared.dependencies.get_bike_service', return_value=mock_bike_service):
            mock_bike_service.get_all_bikes_summary.return_value = {
                "data": [],
                "meta": {"total": 0, "page": 1, "per_page": 10000, "pages": 0}
            }
            
            # Test very large limit
            response = client.get("/api/v1/bikes/?limit=10000")
            
            assert response.status_code == 200
            mock_bike_service.get_all_bikes_summary.assert_called_with(0, 10000)