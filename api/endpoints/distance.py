from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from ..dependencies import BikeServiceDep
from ..schemas import DistanceResponse

router = APIRouter(prefix="/distance", tags=["Distance"])


@router.get("", response_model=list[DistanceResponse])
async def get_all_bikes_distances(service: BikeServiceDep) -> list[DistanceResponse]:
    return service.get_all_distances()


@router.get("/{bike_number}", response_model=DistanceResponse)
async def get_bike_distance(
    bike_number: str, service: BikeServiceDep
) -> DistanceResponse:
    response = service.get_bike_distance(bike_number)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bike not found"
        )

    return response
