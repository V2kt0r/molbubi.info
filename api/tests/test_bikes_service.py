import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from app.bikes.service import BikeService
from app.shared.exceptions import BikeNotFound


class TestBikeService:
    @pytest.fixture
    def mock_bike_repo(self):
        repo = Mock()
        repo.get_movements.return_value = []
        repo.count_movements.return_value = 0
        repo.get_latest_movement.return_value = None
        repo.get_all_summary.return_value = []
        repo.count_all_summary.return_value = 0
        return repo

    @pytest.fixture
    def mock_station_repo(self):
        repo = Mock()
        repo.get_by_uid.return_value = None
        return repo

    @pytest.fixture
    def service(self, mock_bike_repo, mock_station_repo):
        return BikeService(mock_bike_repo, mock_station_repo)

    def test_init(self, mock_bike_repo, mock_station_repo):
        service = BikeService(mock_bike_repo, mock_station_repo)
        assert service.bike_repo == mock_bike_repo
        assert service.station_repo == mock_station_repo

    def test_get_bike_history_empty(self, service, mock_bike_repo):
        mock_bike_repo.get_movements.return_value = []
        mock_bike_repo.count_movements.return_value = 0
        
        result = service.get_bike_history("BIKE123", 0, 25)
        
        mock_bike_repo.get_movements.assert_called_with("BIKE123", 0, 25, 30, None, None)
        mock_bike_repo.count_movements.assert_called_with("BIKE123", 30, None, None)
        
        assert result.data == []
        assert result.meta.total == 0
        assert result.meta.page == 1
        assert result.meta.per_page == 25

    def test_get_bike_history_with_data(self, service, mock_bike_repo):
        # Create mock movement with required attributes
        mock_movement = Mock()
        mock_movement.bike_number = "BIKE123"
        mock_movement.start_time = datetime(2023, 1, 1, 10, 0)
        mock_movement.end_time = datetime(2023, 1, 1, 10, 30)
        mock_movement.distance_km = 2.5
        
        # Create mock stations with proper attributes for Pydantic validation
        mock_start_station = Mock()
        mock_start_station.uid = 1
        mock_start_station.name = "Start Station"
        mock_start_station.lat = 52.5
        mock_start_station.lng = 13.4
        
        mock_end_station = Mock()
        mock_end_station.uid = 2
        mock_end_station.name = "End Station"
        mock_end_station.lat = 52.6
        mock_end_station.lng = 13.5
        
        mock_bike_repo.get_movements.return_value = [(mock_movement, mock_start_station, mock_end_station)]
        mock_bike_repo.count_movements.return_value = 1
        
        result = service.get_bike_history("BIKE123", 0, 25)
        
        assert len(result.data) == 1
        assert result.data[0].bike_number == "BIKE123"
        assert result.data[0].distance_km == 2.5
        assert result.meta.total == 1

    def test_get_bike_history_with_time_filters(self, service, mock_bike_repo):
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        service.get_bike_history("BIKE123", 0, 25, days_back=7, start_date=start_date, end_date=end_date)
        
        mock_bike_repo.get_movements.assert_called_with("BIKE123", 0, 25, 7, start_date, end_date)
        mock_bike_repo.count_movements.assert_called_with("BIKE123", 7, start_date, end_date)

    def test_get_current_location_bike_not_found(self, service, mock_bike_repo):
        mock_bike_repo.get_latest_movement.return_value = None
        
        with pytest.raises(BikeNotFound):
            service.get_current_location("BIKE123")
        
        mock_bike_repo.get_latest_movement.assert_called_with("BIKE123")

    def test_get_current_location_success(self, service, mock_bike_repo, mock_station_repo):
        mock_movement = Mock()
        mock_movement.end_station_uid = 456
        mock_movement.end_time = datetime(2023, 1, 1, 12, 0)
        
        # Create mock station with proper attributes for Pydantic validation
        mock_station = Mock()
        mock_station.uid = 456
        mock_station.name = "Current Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        mock_bike_repo.get_latest_movement.return_value = mock_movement
        mock_station_repo.get_by_uid.return_value = mock_station
        
        result = service.get_current_location("BIKE123")
        
        mock_bike_repo.get_latest_movement.assert_called_with("BIKE123")
        mock_station_repo.get_by_uid.assert_called_with(456)
        
        assert result.bike_number == "BIKE123"
        assert result.current_station.uid == 456
        assert result.current_station.name == "Current Station"
        assert result.last_seen == mock_movement.end_time

    def test_get_all_bikes_summary_empty(self, service, mock_bike_repo):
        mock_bike_repo.get_all_summary.return_value = []
        mock_bike_repo.count_all_summary.return_value = 0
        
        result = service.get_all_bikes_summary(0, 100)
        
        mock_bike_repo.get_all_summary.assert_called_with(0, 100)
        mock_bike_repo.count_all_summary.assert_called()
        
        assert result.data == []
        assert result.meta.total == 0

    def test_get_all_bikes_summary_with_data(self, service, mock_bike_repo):
        # Create mock station with proper attributes for Pydantic validation
        mock_station = Mock()
        mock_station.uid = 1
        mock_station.name = "Test Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        summary_data = [("BIKE123", 5, 12.75, mock_station), ("BIKE456", 3, None, mock_station)]
        
        mock_bike_repo.get_all_summary.return_value = summary_data
        mock_bike_repo.count_all_summary.return_value = 2
        
        result = service.get_all_bikes_summary(0, 100)
        
        assert len(result.data) == 2
        assert result.data[0].bike_number == "BIKE123"
        assert result.data[0].total_trips == 5
        assert result.data[0].total_distance_km == 12.75
        assert result.data[0].current_location.uid == 1
        assert result.data[0].current_location.name == "Test Station"
        
        assert result.data[1].bike_number == "BIKE456"
        assert result.data[1].total_trips == 3
        assert result.data[1].total_distance_km == 0.0  # None should become 0.0
        
        assert result.meta.total == 2

    def test_get_all_bikes_summary_with_pagination(self, service, mock_bike_repo):
        service.get_all_bikes_summary(20, 50)
        
        mock_bike_repo.get_all_summary.assert_called_with(20, 50)

    def test_get_all_bikes_summary_distance_rounding(self, service, mock_bike_repo):
        # Create mock station with proper attributes for Pydantic validation
        mock_station = Mock()
        mock_station.uid = 1
        mock_station.name = "Test Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        summary_data = [("BIKE123", 1, 12.123456, mock_station)]
        
        mock_bike_repo.get_all_summary.return_value = summary_data
        mock_bike_repo.count_all_summary.return_value = 1
        
        result = service.get_all_bikes_summary(0, 100)
        
        assert result.data[0].total_distance_km == 12.12  # Rounded to 2 decimal places