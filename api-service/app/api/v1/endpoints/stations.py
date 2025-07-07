from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi_restful.cbv import cbv

from app.schemas import station as station_schemas
from app.schemas import stay as stay_schema
from app.services.station_service import StationService

from ..dependencies import get_station_service

router = APIRouter()


@cbv(router)
class StationCBV:
    service: StationService = Depends(get_station_service)

    @router.get("/", response_model=List[station_schemas.Station])
    def read_stations(self, skip: int = 0, limit: int = 100):
        return self.service.get_all_stations(skip, limit)

    @router.get("/{station_uid}", response_model=station_schemas.Station)
    def read_station(self, station_uid: int):
        return self.service.get_station_details(station_uid)

    @router.get("/{station_uid}/bikes", response_model=List[str])
    def read_bikes_at_station(self, station_uid: int):
        return self.service.get_bikes_at_station(station_uid)

    @router.get("/{station_uid}/history", response_model=List[stay_schema.BikeStay])
    def read_station_history(self, station_uid: int, at_time: datetime = Query(default_factory=lambda: datetime.now(timezone.utc))):
        """
        Get a list of bikes that were at a specific station at a given point in time.
        The `at_time` should be in ISO 8601 format (e.g., 2024-07-01T14:30:00Z).
        """
        return self.service.get_station_state_at_time(station_uid, at_time)
