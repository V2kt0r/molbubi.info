from fastapi import APIRouter

from ..core.dependencies.services import DistributionServiceDep
from ..schemas.distribution import (
    ArrivalCountByHourResponse,
    HourAndStationArrivalCountResponse,
    StationArrivalCountResponse,
)

router = APIRouter(prefix="/distribution", tags=["Distribution"])


@router.get("/station", response_model=list[StationArrivalCountResponse])
async def get_all_station_distribution(
    service: DistributionServiceDep,
) -> list[StationArrivalCountResponse]:
    return await service.get_all_station_distribution()


@router.get("/hour", response_model=list[ArrivalCountByHourResponse])
async def get_all_station_distribution_by_hour(
    service: DistributionServiceDep,
) -> list[ArrivalCountByHourResponse]:
    return await service.get_distribution_by_hour()


@router.get(
    "/hour-and-station", response_model=list[HourAndStationArrivalCountResponse]
)
async def get_station_and_hour_distribution(
    service: DistributionServiceDep,
) -> list[HourAndStationArrivalCountResponse]:
    return await service.get_hour_and_station_distribution()
