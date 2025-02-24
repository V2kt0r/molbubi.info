from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from ..dependencies import BikeServiceDep
from ..schemas import StationArrivalCountResponse

router = APIRouter(prefix="/station", tags=["Station"])


@router.get("/distribution", response_model=list[StationArrivalCountResponse])
def get_all_station_distribution(
    service: BikeServiceDep,
) -> list[StationArrivalCountResponse]:
    results = service.get_all_station_distribution()
    return sorted(results, key=lambda r: -r.arrival_count)
