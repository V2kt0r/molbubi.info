from datetime import datetime

from app.core.exceptions import StationNotFound
from app.db.repository import BikeStayRepository, RedisRepository, StationRepository
from app.schemas.station import StationStats


class StationService:
    def __init__(self, station_repo: StationRepository, redis_repo: RedisRepository, stay_repo: BikeStayRepository):
        self.station_repo = station_repo
        self.redis_repo = redis_repo
        self.stay_repo = stay_repo

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

    def get_station_state_at_time(self, station_uid: int, at_time: datetime):
        # Verify station exists
        if not self.station_repo.get_by_uid(station_uid):
            raise StationNotFound(station_uid=station_uid)

        # Query bike stays active at the specified time
        stays = self.stay_repo.get_bikes_at_station_at_time(station_uid, at_time)
        # Return list of bike numbers currently at the station at that time
        return stays
        #return [stay.bike_number for stay in stays]

    def get_stations_arrivals_and_departures(self, skip: int = 0, limit: int = 100) -> list[StationStats]:
        """
        Returns a list of StationStats with arrival and departure counts
        for stations, paginated with skip and limit.
        """
        raw_results = self.station_repo.get_arrivals_and_departures(skip=skip, limit=limit)
        
        station_stats = []
        for station, arrival_count, departure_count in raw_results:
            stats = StationStats(
                uid=station.uid,
                name=station.name,
                lat=station.lat,
                lng=station.lng,
                total_arrivals=int(arrival_count),
                total_departures=int(departure_count)
            )
            station_stats.append(stats)
        
        return station_stats
