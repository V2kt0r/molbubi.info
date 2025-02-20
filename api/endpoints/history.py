from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from ..dependencies import BikeServiceDep
from ..schemas import HistoryResponse

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{bike_number}", response_model=HistoryResponse)
def get_bike_history(bike_number: str, bike_service: BikeServiceDep) -> HistoryResponse:
    response = bike_service.get_bike_history(bike_number)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for bike {bike_number}",
        )

    return response
