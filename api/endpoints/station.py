from fastapi import APIRouter

from ..dependencies import BikeServiceDep
from ..schemas import StationArrivalCountResponse

router = APIRouter(prefix="/station", tags=["Station"])


@router.get("/distribution", response_model=list[StationArrivalCountResponse])
def get_all_station_distribution(
    service: BikeServiceDep,
) -> list[StationArrivalCountResponse]:
    return service.get_all_station_distribution()
