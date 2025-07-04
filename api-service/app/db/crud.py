import redis
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.config import settings as api_settings

from . import models

redis_client = redis.Redis(
    host=api_settings.POSTGRES_SERVER.replace("postgres-db", "redis"),
    port=6379,
    decode_responses=True,
)


def get_bikes_at_station(station_uid: int) -> list[str]:
    """Gets the list of bikes currently at a station from Redis."""
    station_key = f"station_bikes:{station_uid}"
    return list(redis_client.smembers(station_key))


# --- Station Queries ---
def get_station(db: Session, station_uid: int):
    return db.query(models.Station).filter(models.Station.uid == station_uid).first()


def get_stations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Station).offset(skip).limit(limit).all()


def get_station_arrival_counts(db: Session, station_uid: int):
    return (
        db.query(func.count(models.BikeMovement.bike_number))
        .filter(models.BikeMovement.end_station_uid == station_uid)
        .scalar()
    )


def get_station_departure_counts(db: Session, station_uid: int):
    return (
        db.query(func.count(models.BikeMovement.bike_number))
        .filter(models.BikeMovement.start_station_uid == station_uid)
        .scalar()
    )


# --- Bike Queries ---
def get_bike_history(db: Session, bike_number: str, skip: int = 0, limit: int = 25):
    return (
        db.query(models.BikeMovement)
        .filter(models.BikeMovement.bike_number == bike_number)
        .order_by(desc(models.BikeMovement.start_time))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_current_bike_location(db: Session, bike_number: str):
    # The last recorded movement for a bike tells us its current location (end_station).
    last_movement = (
        db.query(models.BikeMovement)
        .filter(models.BikeMovement.bike_number == bike_number)
        .order_by(desc(models.BikeMovement.end_time))
        .first()
    )

    if not last_movement:
        return None

    return (
        db.query(models.Station)
        .filter(models.Station.uid == last_movement.end_station_uid)
        .first()
    )


def get_all_bikes_summary(db: Session, skip: int = 0, limit: int = 100):
    """Gets a summary for all bikes (total trips and distance)."""
    # This subquery finds the total trips and distance for each bike
    summary_sq = (
        db.query(
            models.BikeMovement.bike_number,
            func.count(models.BikeMovement.bike_number).label("total_trips"),
            func.sum(models.BikeMovement.distance_km).label("total_distance_km"),
        )
        .group_by(models.BikeMovement.bike_number)
        .subquery()
    )

    # This subquery finds the latest location (end_station_uid) for each bike
    latest_movement_sq = (
        db.query(models.BikeMovement.bike_number, models.BikeMovement.end_station_uid)
        .distinct(models.BikeMovement.bike_number)
        .order_by(models.BikeMovement.bike_number, desc(models.BikeMovement.end_time))
        .subquery()
    )

    # Join the summaries with the latest locations
    results = (
        db.query(
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
            models.Station, models.Station.uid == latest_movement_sq.c.end_station_uid
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results
