from datetime import datetime
import redis
from sqlalchemy import desc, func
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


class RedisRepository:
    def __init__(self):
        redis_host = settings.POSTGRES_SERVER.replace("postgres-db", "redis")
        self.client = redis.Redis(host=redis_host, port=6379, decode_responses=True)

    def get_bikes_at_station(self, station_uid: int) -> list[str]:
        station_key = f"station_bikes:{station_uid}"
        return list(self.client.smembers(station_key))
