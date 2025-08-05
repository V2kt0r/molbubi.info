import pytest
from datetime import datetime
from unittest.mock import Mock
from app.stations.service import StationService
from app.shared.exceptions import StationNotFound


class TestStationService:
    @pytest.fixture
    def mock_station_repo(self):
        repo = Mock()
        repo.get_by_uid.return_value = None
        repo.get_all.return_value = []
        repo.count_all.return_value = 0
        repo.get_arrivals_and_departures.return_value = []
        repo.count_arrivals_and_departures.return_value = 0
        return repo

    @pytest.fixture
    def mock_redis_repo(self):
        repo = Mock()
        repo.get_all_station_bike_counts.return_value = {}
        repo.get_bikes_at_station.return_value = []
        return repo

    @pytest.fixture
    def mock_stay_repo(self):
        repo = Mock()
        repo.get_all_station_bike_counts_at_time.return_value = {}
        repo.get_bikes_at_station_at_time.return_value = []
        return repo

    @pytest.fixture
    def service(self, mock_station_repo, mock_redis_repo, mock_stay_repo):
        return StationService(mock_station_repo, mock_redis_repo, mock_stay_repo)

    def test_init(self, mock_station_repo, mock_redis_repo, mock_stay_repo):
        service = StationService(mock_station_repo, mock_redis_repo, mock_stay_repo)
        assert service.station_repo == mock_station_repo
        assert service.redis_repo == mock_redis_repo
        assert service.stay_repo == mock_stay_repo

    def test_get_station_details_not_found(self, service, mock_station_repo):
        mock_station_repo.get_by_uid.return_value = None
        
        with pytest.raises(StationNotFound):
            service.get_station_details(123)
        
        mock_station_repo.get_by_uid.assert_called_with(123)

    def test_get_station_details_success(self, service, mock_station_repo):
        mock_station = Mock()
        mock_station_repo.get_by_uid.return_value = mock_station
        
        result = service.get_station_details(123)
        
        assert result == mock_station
        mock_station_repo.get_by_uid.assert_called_with(123)

    def test_get_all_stations_with_bike_count_current(self, service, mock_station_repo, mock_redis_repo):
        # Mock station
        mock_station = Mock()
        mock_station.uid = 123
        mock_station.name = "Test Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        mock_station_repo.get_all.return_value = [mock_station]
        mock_station_repo.count_all.return_value = 1
        mock_redis_repo.get_all_station_bike_counts.return_value = {123: 5}
        
        result = service.get_all_stations_with_bike_count(0, 100)
        
        mock_redis_repo.get_all_station_bike_counts.assert_called()
        mock_station_repo.get_all.assert_called_with(skip=0, limit=10000)
        
        assert len(result.data) == 1
        assert result.data[0].uid == 123
        assert result.data[0].bike_count == 5
        assert result.meta.total == 1

    def test_get_all_stations_with_bike_count_historical(self, service, mock_station_repo, mock_stay_repo):
        at_time = datetime(2023, 1, 1, 12, 0)
        mock_station = Mock()
        mock_station.uid = 456
        mock_station.name = "Historical Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        mock_station_repo.get_all.return_value = [mock_station]
        mock_station_repo.count_all.return_value = 1
        mock_stay_repo.get_all_station_bike_counts_at_time.return_value = {456: 3}
        
        result = service.get_all_stations_with_bike_count(0, 100, at_time=at_time)
        
        mock_stay_repo.get_all_station_bike_counts_at_time.assert_called_with(at_time)
        
        assert len(result.data) == 1
        assert result.data[0].uid == 456
        assert result.data[0].bike_count == 3

    def test_get_all_stations_with_bike_count_zero_bikes(self, service, mock_station_repo, mock_redis_repo):
        mock_station = Mock()
        mock_station.uid = 789
        mock_station.name = "Empty Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        mock_station_repo.get_all.return_value = [mock_station]
        mock_station_repo.count_all.return_value = 1
        mock_redis_repo.get_all_station_bike_counts.return_value = {}  # No bikes at any station
        
        result = service.get_all_stations_with_bike_count(0, 100)
        
        assert len(result.data) == 1
        assert result.data[0].bike_count == 0

    def test_get_all_stations_with_bike_count_sorting(self, service, mock_station_repo, mock_redis_repo):
        station1 = Mock()
        station1.uid = 1
        station1.name = "Station 1"
        station1.lat = 52.5
        station1.lng = 13.4
        
        station2 = Mock()
        station2.uid = 2
        station2.name = "Station 2"
        station2.lat = 52.5
        station2.lng = 13.4
        
        mock_station_repo.get_all.return_value = [station1, station2]
        mock_station_repo.count_all.return_value = 2
        mock_redis_repo.get_all_station_bike_counts.return_value = {1: 3, 2: 7}  # Station 2 has more bikes
        
        result = service.get_all_stations_with_bike_count(0, 100)
        
        assert len(result.data) == 2
        assert result.data[0].uid == 2  # Station 2 should be first (7 bikes)
        assert result.data[0].bike_count == 7
        assert result.data[1].uid == 1  # Station 1 should be second (3 bikes)
        assert result.data[1].bike_count == 3

    def test_get_all_stations_with_bike_count_pagination(self, service, mock_station_repo, mock_redis_repo):
        stations = []
        for i in range(5):
            station = Mock()
            station.uid = i
            station.name = f"Station {i}"
            station.lat = 52.5
            station.lng = 13.4
            stations.append(station)
        
        mock_station_repo.get_all.return_value = stations
        mock_station_repo.count_all.return_value = 5
        mock_redis_repo.get_all_station_bike_counts.return_value = {i: i for i in range(5)}
        
        result = service.get_all_stations_with_bike_count(skip=2, limit=2)
        
        assert len(result.data) == 2
        assert result.meta.total == 5

    def test_get_bikes_at_station_not_found(self, service, mock_station_repo):
        mock_station_repo.get_by_uid.return_value = None
        
        with pytest.raises(StationNotFound):
            service.get_bikes_at_station(123)
        
        mock_station_repo.get_by_uid.assert_called_with(123)

    def test_get_bikes_at_station_current(self, service, mock_station_repo, mock_redis_repo):
        mock_station_repo.get_by_uid.return_value = Mock()
        mock_redis_repo.get_bikes_at_station.return_value = ["bike1", "bike2"]
        
        result = service.get_bikes_at_station(123)
        
        mock_redis_repo.get_bikes_at_station.assert_called_with(123)
        assert result == ["bike1", "bike2"]

    def test_get_bikes_at_station_historical(self, service, mock_station_repo, mock_stay_repo):
        at_time = datetime(2023, 1, 1, 12, 0)
        mock_station_repo.get_by_uid.return_value = Mock()
        
        mock_stay1 = Mock()
        mock_stay1.bike_number = "bike1"
        mock_stay2 = Mock()
        mock_stay2.bike_number = "bike2"
        
        mock_stay_repo.get_bikes_at_station_at_time.return_value = [mock_stay1, mock_stay2]
        
        result = service.get_bikes_at_station(123, at_time=at_time)
        
        mock_stay_repo.get_bikes_at_station_at_time.assert_called_with(123, at_time)
        assert result == ["bike1", "bike2"]

    def test_get_station_state_at_time_not_found(self, service, mock_station_repo):
        at_time = datetime(2023, 1, 1, 12, 0)
        mock_station_repo.get_by_uid.return_value = None
        
        with pytest.raises(StationNotFound):
            service.get_station_state_at_time(123, at_time)

    def test_get_station_state_at_time_success(self, service, mock_station_repo, mock_stay_repo):
        at_time = datetime(2023, 1, 1, 12, 0)
        mock_station_repo.get_by_uid.return_value = Mock()
        mock_stays = [Mock(), Mock()]
        mock_stay_repo.get_bikes_at_station_at_time.return_value = mock_stays
        
        result = service.get_station_state_at_time(123, at_time)
        
        mock_stay_repo.get_bikes_at_station_at_time.assert_called_with(123, at_time)
        assert result == mock_stays

    def test_get_stations_arrivals_and_departures(self, service, mock_station_repo):
        mock_station = Mock()
        mock_station.uid = 123
        mock_station.name = "Test Station"
        mock_station.lat = 52.5
        mock_station.lng = 13.4
        
        mock_station_repo.get_arrivals_and_departures.return_value = [(mock_station, 10, 8)]
        mock_station_repo.count_arrivals_and_departures.return_value = 1
        
        result = service.get_stations_arrivals_and_departures(0, 100)
        
        mock_station_repo.get_arrivals_and_departures.assert_called_with(skip=0, limit=100)
        mock_station_repo.count_arrivals_and_departures.assert_called()
        
        assert len(result.data) == 1
        assert result.data[0].uid == 123
        assert result.data[0].total_arrivals == 10
        assert result.data[0].total_departures == 8
        assert result.meta.total == 1

    def test_get_stations_arrivals_and_departures_pagination(self, service, mock_station_repo):
        service.get_stations_arrivals_and_departures(skip=20, limit=50)
        
        mock_station_repo.get_arrivals_and_departures.assert_called_with(skip=20, limit=50)