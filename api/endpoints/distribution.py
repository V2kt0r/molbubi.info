from fastapi import APIRouter

from ..dependencies import BikeServiceDep
from ..schemas import (
    ArrivalCountByHourResponse,
    HourAndStationArrivalCountResponse,
    StationArrivalCountResponse,
)

router = APIRouter(prefix="/distribution", tags=["Distribution"])


@router.get("/station", response_model=list[StationArrivalCountResponse])
def get_all_station_distribution(
    service: BikeServiceDep,
) -> list[StationArrivalCountResponse]:
    return service.get_all_station_distribution()


@router.get("/hour", response_model=list[ArrivalCountByHourResponse])
def get_all_station_distribution_by_hour(
    service: BikeServiceDep,
) -> list[ArrivalCountByHourResponse]:
    return service.get_distribution_by_hour()


@router.get(
    "/hour-and-station", response_model=list[HourAndStationArrivalCountResponse]
)
def get_station_and_hour_distribution(
    service: BikeServiceDep,
) -> list[HourAndStationArrivalCountResponse]:
    return service.get_hour_and_station_distribution()
