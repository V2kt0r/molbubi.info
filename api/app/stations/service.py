from datetime import datetime

from app.shared.exceptions import StationNotFound
from app.stations.repository import BikeStayRepository, RedisRepository, StationRepository
from app.stations.schema import StationStats, StationBikeCount
from app.shared.schemas import PaginatedResponse, create_pagination_meta


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

    def get_all_stations_with_bike_count(self, skip: int, limit: int, at_time: datetime = None) -> PaginatedResponse[StationBikeCount]:
        """
        Get all stations with their current bike counts, ordered by count descending.
        If at_time is provided, returns bike counts at that specific time from historical data.
        If at_time is not provided, returns current bike counts from Redis.
        """
        if at_time is None:
            # Get current bike counts from Redis
            bike_counts = self.redis_repo.get_all_station_bike_counts()
        else:
            # Get historical bike counts from database
            bike_counts = self.stay_repo.get_all_station_bike_counts_at_time(at_time)

        # Get all stations and combine with bike counts
        all_stations = self.station_repo.get_all(skip=0, limit=10000)  # Get all to filter and sort
        total_count = self.station_repo.count_all()
        
        stations_with_counts = []
        for station in all_stations:
            bike_count = bike_counts.get(station.uid, 0)
            station_with_count = StationBikeCount(
                uid=station.uid,
                name=station.name,
                lat=station.lat,
                lng=station.lng,
                bike_count=bike_count
            )
            stations_with_counts.append(station_with_count)
        
        # Sort by bike count descending
        stations_with_counts.sort(key=lambda x: x.bike_count, reverse=True)
        
        # Apply pagination
        paginated_data = stations_with_counts[skip:skip + limit]
        meta = create_pagination_meta(skip, limit, total_count)
        
        return PaginatedResponse(data=paginated_data, meta=meta)

    def get_bikes_at_station(self, station_uid: int, at_time: datetime = None):
        if not self.station_repo.get_by_uid(station_uid):
            raise StationNotFound(station_uid=station_uid)
        
        if at_time is None:
            # Return current bikes from Redis
            return self.redis_repo.get_bikes_at_station(station_uid)
        else:
            # Return historical bikes from database
            stays = self.stay_repo.get_bikes_at_station_at_time(station_uid, at_time)
            return [stay.bike_number for stay in stays]

    def get_station_state_at_time(self, station_uid: int, at_time: datetime):
        # Verify station exists
        if not self.station_repo.get_by_uid(station_uid):
            raise StationNotFound(station_uid=station_uid)

        # Query bike stays active at the specified time
        stays = self.stay_repo.get_bikes_at_station_at_time(station_uid, at_time)
        # Return list of bike numbers currently at the station at that time
        return stays
        #return [stay.bike_number for stay in stays]

    def get_stations_arrivals_and_departures(self, skip: int = 0, limit: int = 100) -> PaginatedResponse[StationStats]:
        """
        Returns a paginated list of StationStats with arrival and departure counts
        for stations.
        """
        raw_results = self.station_repo.get_arrivals_and_departures(skip=skip, limit=limit)
        total_count = self.station_repo.count_arrivals_and_departures()
        
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
        
        meta = create_pagination_meta(skip, limit, total_count)
        return PaginatedResponse(data=station_stats, meta=meta)

