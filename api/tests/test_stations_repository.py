import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Query
from app.stations.repository import StationRepository, BikeStayRepository, RedisRepository


class TestStationRepository:
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        query_mock.count.return_value = 0
        query_mock.group_by.return_value = query_mock
        query_mock.subquery.return_value = Mock()
        query_mock.outerjoin.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        
        db.query.return_value = query_mock
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return StationRepository(mock_db)

    def test_init(self, mock_db):
        repo = StationRepository(mock_db)
        assert repo.db == mock_db

    def test_get_by_uid(self, repository, mock_db):
        result = repository.get_by_uid(123)
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.first.assert_called()

    def test_get_all_default_pagination(self, repository, mock_db):
        result = repository.get_all()
        
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(0)
        query_mock.limit.assert_called_with(100)
        query_mock.all.assert_called()

    def test_get_all_custom_pagination(self, repository, mock_db):
        repository.get_all(skip=20, limit=50)
        
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(20)
        query_mock.limit.assert_called_with(50)

    def test_count_all(self, repository, mock_db):
        result = repository.count_all()
        
        query_mock = mock_db.query.return_value
        query_mock.count.assert_called()

    def test_get_arrivals_and_departures(self, repository, mock_db):
        result = repository.get_arrivals_and_departures()
        
        # Should make multiple query calls for subqueries
        assert mock_db.query.call_count >= 1
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(0)
        query_mock.limit.assert_called_with(100)

    def test_get_arrivals_and_departures_custom_pagination(self, repository, mock_db):
        repository.get_arrivals_and_departures(skip=10, limit=25)
        
        query_mock = mock_db.query.return_value
        query_mock.offset.assert_called_with(10)
        query_mock.limit.assert_called_with(25)

    def test_count_arrivals_and_departures(self, repository, mock_db):
        result = repository.count_arrivals_and_departures()
        
        query_mock = mock_db.query.return_value
        query_mock.count.assert_called()


class TestBikeStayRepository:
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = []
        query_mock.group_by.return_value = query_mock
        
        db.query.return_value = query_mock
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return BikeStayRepository(mock_db)

    def test_init(self, mock_db):
        repo = BikeStayRepository(mock_db)
        assert repo.db == mock_db

    def test_get_bikes_at_station_at_time(self, repository, mock_db):
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        result = repository.get_bikes_at_station_at_time(123, timestamp)
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.all.assert_called()

    def test_get_all_station_bike_counts_at_time(self, repository, mock_db):
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_db.query.return_value.all.return_value = [(123, 5), (456, 3)]
        
        result = repository.get_all_station_bike_counts_at_time(timestamp)
        
        query_mock = mock_db.query.return_value
        query_mock.filter.assert_called()
        query_mock.group_by.assert_called()
        query_mock.all.assert_called()
        
        assert result == {123: 5, 456: 3}

    def test_get_all_station_bike_counts_at_time_empty(self, repository, mock_db):
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_db.query.return_value.all.return_value = []
        
        result = repository.get_all_station_bike_counts_at_time(timestamp)
        
        assert result == {}


class TestRedisRepository:
    @pytest.fixture
    def mock_redis(self):
        with patch('app.stations.repository.__import__') as mock_import:
            mock_redis_module = Mock()
            mock_redis_client = Mock()
            mock_redis_module.Redis.return_value = mock_redis_client
            mock_import.return_value = mock_redis_module
            
            mock_redis_client.smembers.return_value = {"bike1", "bike2"}
            mock_redis_client.scan_iter.return_value = ["station_bikes:123", "station_bikes:456"]
            mock_redis_client.scard.return_value = 5
            
            yield mock_redis_client

    @pytest.fixture
    def mock_settings(self):
        with patch('app.stations.repository.settings') as mock_settings:
            mock_settings.REDIS_HOST = "localhost"
            mock_settings.REDIS_DOCKER_PORT = 6379
            mock_settings.REDIS_STATION_BIKES_SET_PREFIX = "station_bikes"
            yield mock_settings

    def test_init_default_params(self, mock_redis, mock_settings):
        repo = RedisRepository()
        # Should use settings values

    def test_init_custom_params(self, mock_redis, mock_settings):
        repo = RedisRepository(host="custom-host", port=9999)
        # Should use provided values

    def test_get_bikes_at_station(self, mock_redis, mock_settings):
        mock_redis.smembers.return_value = {"bike1", "bike2", "bike3"}
        
        repo = RedisRepository()
        result = repo.get_bikes_at_station(123)
        
        mock_redis.smembers.assert_called_with("station_bikes:123")
        assert result == ["bike1", "bike2", "bike3"]

    def test_get_all_station_bike_counts(self, mock_redis, mock_settings):
        mock_redis.scan_iter.return_value = ["station_bikes:123", "station_bikes:456", "invalid:key"]
        mock_redis.scard.side_effect = lambda key: {"station_bikes:123": 5, "station_bikes:456": 3}.get(key, 0)
        
        repo = RedisRepository()
        result = repo.get_all_station_bike_counts()
        
        mock_redis.scan_iter.assert_called_with(match="station_bikes:*")
        assert result == {123: 5, 456: 3}

    def test_get_all_station_bike_counts_invalid_keys(self, mock_redis, mock_settings):
        mock_redis.scan_iter.return_value = ["invalid:key", "station_bikes:invalid"]
        
        repo = RedisRepository()
        result = repo.get_all_station_bike_counts()
        
        assert result == {}

    def test_get_all_station_bike_counts_empty(self, mock_redis, mock_settings):
        mock_redis.scan_iter.return_value = []
        
        repo = RedisRepository()
        result = repo.get_all_station_bike_counts()
        
        assert result == {}