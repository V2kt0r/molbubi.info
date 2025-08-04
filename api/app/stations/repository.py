from sqlalchemy import desc, func

from app.shared.repository import BaseRepository
from shared_models.models import Station, BikeMovement, BikeStay


class StationRepository(BaseRepository):
    def get_by_uid(self, station_uid: int):
        return (
            self.db.query(Station)
            .filter(Station.uid == station_uid)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Station).offset(skip).limit(limit).all()
    
    def count_all(self) -> int:
        return self.db.query(Station).count()

    def get_arrivals_and_departures(self, skip: int = 0, limit: int = 100) -> list[tuple]:
        """
        Returns a list of stations with their arrival and departure counts.

        Each item in the list is a tuple:
        (Station instance, arrival_count: int, departure_count: int)

        - arrival_count counts how many bikes ended their trips at this station.
        - departure_count counts how many bikes started their trips at this station.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Number of records to return

        Returns:
            list of tuples (Station, arrival_count, departure_count)
        """
        arrival_counts = (
            self.db.query(
                BikeMovement.end_station_uid.label("station_uid"),
                func.count(BikeMovement.bike_number).label("arrival_count"),
            )
            .filter(BikeMovement.end_station_uid.isnot(None))
            .group_by(BikeMovement.end_station_uid)
            .subquery()
        )

        departure_counts = (
            self.db.query(
                BikeMovement.start_station_uid.label("station_uid"),
                func.count(BikeMovement.bike_number).label("departure_count"),
            )
            .filter(BikeMovement.start_station_uid.isnot(None))
            .group_by(BikeMovement.start_station_uid)
            .subquery()
        )

        # Join stations with arrivals and departures counts
        query = (
            self.db.query(
                Station,
                func.coalesce(arrival_counts.c.arrival_count, 0).label("arrival_count"),
                func.coalesce(departure_counts.c.departure_count, 0).label("departure_count"),
            )
            .outerjoin(arrival_counts, Station.uid == arrival_counts.c.station_uid)
            .outerjoin(departure_counts, Station.uid == departure_counts.c.station_uid)
            .order_by(desc(func.coalesce(arrival_counts.c.arrival_count, 0)))
            .offset(skip)
            .limit(limit)
        )

        return query.all()
        
    def count_arrivals_and_departures(self) -> int:
        """Count all stations for arrivals and departures pagination"""
        return self.db.query(Station).count()


class BikeStayRepository(BaseRepository):
    def get_bikes_at_station_at_time(self, station_uid: int, timestamp):
        """
        Finds all bike stays that were active at a specific station at a specific time.
        """
        return self.db.query(BikeStay).filter(
            BikeStay.station_uid == station_uid,
            BikeStay.start_time <= timestamp,
            (BikeStay.end_time == None) | (BikeStay.end_time >= timestamp)
        ).all()

    def get_all_station_bike_counts_at_time(self, timestamp) -> dict[int, int]:
        """
        Get bike counts for all stations at a specific time from historical data.
        Returns a dictionary mapping station_uid to bike_count.
        """
        # Query to count bikes at each station at the specified time
        result = self.db.query(
            BikeStay.station_uid,
            func.count(BikeStay.bike_number).label('bike_count')
        ).filter(
            BikeStay.start_time <= timestamp,
            (BikeStay.end_time == None) | (BikeStay.end_time >= timestamp)
        ).group_by(BikeStay.station_uid).all()
        
        # Convert to dictionary
        return {station_uid: bike_count for station_uid, bike_count in result}


class RedisRepository:
    def __init__(self, host: str = None, port: int = None):
        from app.core.config import settings
        self.client = __import__('redis').Redis(
            host=host or settings.REDIS_HOST, 
            port=port or settings.REDIS_DOCKER_PORT, 
            decode_responses=True
        )

    def get_bikes_at_station(self, station_uid: int) -> list[str]:
        from app.core.config import settings
        station_key = f"{settings.REDIS_STATION_BIKES_SET_PREFIX}:{station_uid}"
        return list(self.client.smembers(station_key))

    def get_all_station_bike_counts(self) -> dict[int, int]:
        """
        Get bike counts for all stations from Redis.
        Returns a dictionary mapping station_uid to bike_count.
        """
        from app.core.config import settings
        pattern = f"{settings.REDIS_STATION_BIKES_SET_PREFIX}:*"
        station_counts = {}
        
        for key in self.client.scan_iter(match=pattern):
            try:
                # Extract station_uid from key like "station_bikes:42990796"
                station_uid = int(key.split(':')[-1])
                bike_count = self.client.scard(key)
                station_counts[station_uid] = bike_count
            except (ValueError, IndexError):
                # Skip invalid keys
                continue
                
        return station_counts