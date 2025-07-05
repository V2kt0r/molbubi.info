from app.core.exceptions import StationNotFound
from app.db.repository import RedisRepository, StationRepository


class StationService:
    def __init__(self, station_repo: StationRepository, redis_repo: RedisRepository):
        self.station_repo = station_repo
        self.redis_repo = redis_repo

    def get_station_details(self, station_uid: int):
        db_station = self.station_repo.get_by_uid(station_uid)
        if not db_station:
            raise StationNotFound(station_uid=station_uid)
        return db_station

    def get_all_stations(self, skip: int, limit: int):
        return self.station_repo.get_all(skip=skip, limit=limit)

    def get_bikes_at_station(self, station_uid: int):
        if not self.station_repo.get_by_uid(station_uid):
            raise StationNotFound(station_uid=station_uid)
        return self.redis_repo.get_bikes_at_station(station_uid)
