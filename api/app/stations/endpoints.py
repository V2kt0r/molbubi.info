from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi_restful.cbv import cbv

from app.stations import schema as station_schemas
from app.stations.stay_schema import BikeStay
from app.stations.service import StationService
from app.shared.dependencies import get_station_service
from app.shared.schemas import PaginatedResponse

router = APIRouter()


@cbv(router)
class StationCBV:
    service: StationService = Depends(get_station_service)

    @router.get("/", response_model=PaginatedResponse[station_schemas.StationBikeCount])
    def read_stations(self, skip: int = 0, limit: int = 100, at_time: datetime = Query(default=None)):
        """
        Get all stations with their current bike counts, ordered by count descending.
        If at_time is provided, returns bike counts at that specific time from historical data.
        If at_time is not provided, returns current bike counts from Redis.
        The `at_time` should be in ISO 8601 format (e.g., 2024-07-01T14:30:00Z).
        """
        return self.service.get_all_stations_with_bike_count(skip, limit, at_time)

    @router.get("/arrivals", response_model=PaginatedResponse[station_schemas.StationStats])
    def read_stations_arrivals(self, skip: int = 0, limit: int = 100):
        """
        Get all stations with their arrival and departure statistics.
        Returns station information along with total arrivals and departures counts.
        """
        return self.service.get_stations_arrivals_and_departures(skip, limit)


    @router.get("/{station_uid}", response_model=station_schemas.Station)
    def read_station(self, station_uid: int):
        return self.service.get_station_details(station_uid)

    @router.get("/{station_uid}/bikes", response_model=list[str])
    def read_bikes_at_station(self, station_uid: int, at_time: datetime = Query(default=None)):
        """
        Get a list of bikes at a specific station.
        If at_time is provided, returns bikes at that specific time from historical data.
        If at_time is not provided, returns current bikes at the station from Redis.
        The `at_time` should be in ISO 8601 format (e.g., 2024-07-01T14:30:00Z).
        """
        return self.service.get_bikes_at_station(station_uid, at_time)

    @router.get("/{station_uid}/history", response_model=list[BikeStay])
    def read_station_history(self, station_uid: int, at_time: datetime = Query(default_factory=lambda: datetime.now(timezone.utc))):
        """
        Get a list of bikes that were at a specific station at a given point in time.
        The `at_time` should be in ISO 8601 format (e.g., 2024-07-01T14:30:00Z).
        """
        return self.service.get_station_state_at_time(station_uid, at_time)
