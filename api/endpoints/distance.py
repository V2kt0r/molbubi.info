from fastapi import APIRouter

from ..core.dependencies.services import DistanceServiceDep
from ..core.exceptions import BikeNotFoundException
from ..schemas.distance import DistanceResponse

router = APIRouter(prefix="/distance", tags=["Distance"])


@router.get("", response_model=list[DistanceResponse])
async def get_all_bikes_distances(service: DistanceServiceDep):
    return await service.get_all_distances()


@router.get("/{bike_number}", response_model=DistanceResponse)
async def get_bike_distance(bike_number: str, service: DistanceServiceDep):
    response = await service.get_bike_distance(bike_number)

    if not response:
        raise BikeNotFoundException(bike_number)

    return response
