from fastapi import APIRouter

from ..core.dependencies.services import HistoryServiceDep
from ..core.exceptions import BikeNotFoundException
from ..schemas.history import HistoryResponse

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{bike_number}", response_model=HistoryResponse)
async def get_bike_history(
    bike_number: str, history_service: HistoryServiceDep
) -> HistoryResponse:
    response = await history_service.get_bike_history(bike_number)

    if not response:
        raise BikeNotFoundException(bike_number)

    return response
