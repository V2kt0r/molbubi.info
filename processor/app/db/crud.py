import datetime

from sqlalchemy.orm import Session

from app.schemas.bike_data import Station as StationSchema

from . import models


def upsert_station(db: Session, station: StationSchema):
    """Create or update a station."""
    db_station = (
        db.query(models.Station).filter(models.Station.uid == station.uid).first()
    )
    if not db_station:
        db_station = models.Station(
            uid=station.uid, name=station.name, lat=station.lat, lng=station.lng
        )
        db.add(db_station)
    else:
        db_station.name = station.name
        db_station.lat = station.lat
        db_station.lng = station.lng
    db.commit()
    db.refresh(db_station)
    return db_station


def create_bike_movement(
    db: Session,
    bike_number: str,
    start_station_uid: int,
    end_station_uid: int,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    distance_km: float,
):
    """Create a new bike movement record."""
    db_movement = models.BikeMovement(
        bike_number=bike_number,
        start_station_uid=start_station_uid,
        end_station_uid=end_station_uid,
        start_time=start_time,
        end_time=end_time,
        distance_km=distance_km,
    )
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement
