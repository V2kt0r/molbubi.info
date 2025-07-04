from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import crud
from app.db.database import get_db
from app.schemas import station as station_schemas

router = APIRouter()


@router.get("/", response_model=List[station_schemas.Station])
def read_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stations = crud.get_stations(db, skip=skip, limit=limit)
    return stations


@router.get("/{station_uid}", response_model=station_schemas.Station)
def read_station(station_uid: int, db: Session = Depends(get_db)):
    db_station = crud.get_station(db, station_uid=station_uid)
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station


@router.get("/{station_uid}/stats", response_model=station_schemas.StationStats)
def read_station_stats(station_uid: int, db: Session = Depends(get_db)):
    arrivals = crud.get_station_arrival_counts(db, station_uid=station_uid)
    departures = crud.get_station_departure_counts(db, station_uid=station_uid)
    return {"total_arrivals": arrivals, "total_departures": departures}


@router.get("/{station_uid}/bikes", response_model=List[str])
def read_bikes_at_station(station_uid: int):
    """
    Get a list of bike numbers currently at a specific station (real-time).
    """
    bike_numbers = crud.get_bikes_at_station(station_uid=station_uid)
    if not bike_numbers and not crud.get_station(
        next(get_db()), station_uid=station_uid
    ):
        # If the station doesn't exist at all, raise 404
        raise HTTPException(status_code=404, detail="Station not found")
    return bike_numbers
