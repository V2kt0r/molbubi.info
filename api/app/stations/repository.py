from sqlalchemy import desc, func

from app.shared.repository import BaseRepository
from app.shared import models


class StationRepository(BaseRepository):
    def get_by_uid(self, station_uid: int):
        return (
            self.db.query(models.Station)
            .filter(models.Station.uid == station_uid)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.Station).offset(skip).limit(limit).all()

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
                models.BikeMovement.end_station_uid.label("station_uid"),
                func.count(models.BikeMovement.bike_number).label("arrival_count"),
            )
            .filter(models.BikeMovement.end_station_uid.isnot(None))
            .group_by(models.BikeMovement.end_station_uid)
            .subquery()
        )

        departure_counts = (
            self.db.query(
                models.BikeMovement.start_station_uid.label("station_uid"),
                func.count(models.BikeMovement.bike_number).label("departure_count"),
            )
            .filter(models.BikeMovement.start_station_uid.isnot(None))
            .group_by(models.BikeMovement.start_station_uid)
            .subquery()
        )

        # Join stations with arrivals and departures counts
        query = (
            self.db.query(
                models.Station,
                func.coalesce(arrival_counts.c.arrival_count, 0).label("arrival_count"),
                func.coalesce(departure_counts.c.departure_count, 0).label("departure_count"),
            )
            .outerjoin(arrival_counts, models.Station.uid == arrival_counts.c.station_uid)
            .outerjoin(departure_counts, models.Station.uid == departure_counts.c.station_uid)
            .order_by(desc(func.coalesce(arrival_counts.c.arrival_count, 0)))
            .offset(skip)
            .limit(limit)
        )

        return query.all()


class BikeStayRepository(BaseRepository):
    def get_bikes_at_station_at_time(self, station_uid: int, timestamp):
        """
        Finds all bike stays that were active at a specific station at a specific time.
        """
        return self.db.query(models.BikeStay).filter(
            models.BikeStay.station_uid == station_uid,
            models.BikeStay.start_time <= timestamp,
            (models.BikeStay.end_time == None) | (models.BikeStay.end_time >= timestamp)
        ).all()


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