from typing import List

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from app.schemas import station as station_schemas
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
