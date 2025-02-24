from fastapi import APIRouter

from ..dependencies import BikeServiceDep
from ..schemas import ArrivalCountByHourResponse, StationArrivalCountResponse

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
