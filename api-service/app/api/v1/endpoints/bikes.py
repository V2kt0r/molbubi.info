from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import crud
from app.db.database import get_db
from app.schemas import bike as bike_schemas

router = APIRouter()


@router.get("/", response_model=List[bike_schemas.BikeSummary])
def read_all_bikes_summary(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a summary for all bikes, including trip counts and location.
    """
    summaries = crud.get_all_bikes_summary(db, skip=skip, limit=limit)

    # The CRUD function returns a tuple, we need to map it to the Pydantic model
    result_list = []
    for bike_number, total_trips, total_distance_km, station in summaries:
        result_list.append(
            bike_schemas.BikeSummary(
                bike_number=bike_number,
                total_trips=total_trips,
                total_distance_km=(
                    round(total_distance_km, 2) if total_distance_km else 0.0
                ),
                current_location=station,
            )
        )
    return result_list


@router.get("/{bike_number}/history", response_model=List[bike_schemas.BikeMovement])
def read_bike_history(
    bike_number: str, skip: int = 0, limit: int = 25, db: Session = Depends(get_db)
):
    history = crud.get_bike_history(db, bike_number=bike_number, skip=skip, limit=limit)
    return history


@router.get("/{bike_number}/location", response_model=bike_schemas.BikeLocation)
def read_bike_location(bike_number: str, db: Session = Depends(get_db)):
    station = crud.get_current_bike_location(db, bike_number=bike_number)
    if not station:
        raise HTTPException(status_code=404, detail="Location for this bike not found")

    last_movement = crud.get_bike_history(db, bike_number=bike_number, limit=1)[0]

    return {
        "bike_number": bike_number,
        "current_station": station,
        "last_seen": last_movement.end_time,
    }
