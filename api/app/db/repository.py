from datetime import datetime, date
import redis
from sqlalchemy import desc, func, extract
from sqlalchemy.orm import Session

from app.core.config import settings

from . import models


class BaseRepository:
    def __init__(self, db_session: Session):
        self.db = db_session


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


class BikeRepository(BaseRepository):
    def get_movements(self, bike_number: str, skip: int = 0, limit: int = 25):
        return (
            self.db.query(models.BikeMovement)
            .filter(models.BikeMovement.bike_number == bike_number)
            .order_by(desc(models.BikeMovement.start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_movement(self, bike_number: str):
        return (
            self.db.query(models.BikeMovement)
            .filter(models.BikeMovement.bike_number == bike_number)
            .order_by(desc(models.BikeMovement.end_time))
            .first()
        )

    def get_all_summary(self, skip: int = 0, limit: int = 100):
        summary_sq = (
            self.db.query(
                models.BikeMovement.bike_number,
                func.count().label("total_trips"),
                func.sum(models.BikeMovement.distance_km).label("total_distance_km"),
            )
            .group_by(models.BikeMovement.bike_number)
            .subquery()
        )

        latest_movement_sq = (
            self.db.query(
                models.BikeMovement.bike_number, models.BikeMovement.end_station_uid
            )
            .distinct(models.BikeMovement.bike_number)
            .order_by(
                models.BikeMovement.bike_number, desc(models.BikeMovement.end_time)
            )
            .subquery()
        )

        return (
            self.db.query(
                summary_sq.c.bike_number,
                summary_sq.c.total_trips,
                summary_sq.c.total_distance_km,
                models.Station,
            )
            .join(
                latest_movement_sq,
                latest_movement_sq.c.bike_number == summary_sq.c.bike_number,
            )
            .join(
                models.Station,
                models.Station.uid == latest_movement_sq.c.end_station_uid,
            )
            .order_by(desc(summary_sq.c.total_distance_km))
            .offset(skip)
            .limit(limit)
            .all()
        )


class BikeStayRepository(BaseRepository):
    def get_bikes_at_station_at_time(self, station_uid: int, timestamp: datetime):
        """
        Finds all bike stays that were active at a specific station at a specific time.
        """
        return self.db.query(models.BikeStay).filter(
            models.BikeStay.station_uid == station_uid,
            models.BikeStay.start_time <= timestamp,
            (models.BikeStay.end_time == None) | (models.BikeStay.end_time >= timestamp)
        ).all()


class DistributionRepository(BaseRepository):
    def get_hourly_arrival_distribution(
        self, 
        start_date: date | None = None, 
        end_date: date | None = None, 
        station_uids: list[int] | None = None
    ) -> list[dict]:
        """
        Get hourly distribution of bike arrivals.
        
        Args:
            start_date: Filter arrivals from this date (inclusive)
            end_date: Filter arrivals until this date (inclusive)  
            station_uids: Filter arrivals to specific stations
            
        Returns:
            List of dicts with 'time' (hour 0-23) and 'arrival_count'
        """
        query = self.db.query(
            extract('hour', models.BikeMovement.end_time).label('hour'),
            func.count(models.BikeMovement.bike_number).label('arrival_count')
        ).filter(
            models.BikeMovement.end_time.isnot(None),
            models.BikeMovement.end_station_uid.isnot(None)
        )
        
        # Apply date range filter
        if start_date:
            query = query.filter(func.date(models.BikeMovement.end_time) >= start_date)
        if end_date:
            query = query.filter(func.date(models.BikeMovement.end_time) <= end_date)
            
        # Apply station filter
        if station_uids:
            query = query.filter(models.BikeMovement.end_station_uid.in_(station_uids))
            
        results = query.group_by(extract('hour', models.BikeMovement.end_time)).all()
        
        # Create a complete 24-hour distribution (fill missing hours with 0)
        hour_counts = {int(hour): count for hour, count in results}
        distribution = []
        for hour in range(24):
            distribution.append({
                'time': hour,
                'arrival_count': hour_counts.get(hour, 0)
            })
            
        return distribution


class RedisRepository:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_DOCKER_PORT):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def get_bikes_at_station(self, station_uid: int) -> list[str]:
        station_key = f"{settings.REDIS_STATION_BIKES_SET_PREFIX}:{station_uid}"
        return list(self.client.smembers(station_key))
