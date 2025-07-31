from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from app.bikes import schema as bike_schemas
from app.bikes.service import BikeService
from app.shared.dependencies import get_bike_service

router = APIRouter()


@cbv(router)
class BikeCBV:
    service: BikeService = Depends(get_bike_service)

    @router.get("/", response_model=list[bike_schemas.BikeSummary])
    def read_all_bikes_summary(self, skip: int = 0, limit: int = 100):
        return self.service.get_all_bikes_summary(skip, limit)

    @router.get(
        "/{bike_number}/history", response_model=list[bike_schemas.BikeMovement]
    )
    def read_bike_history(self, bike_number: str, skip: int = 0, limit: int = 25):
        return self.service.get_bike_history(bike_number, skip, limit)

    @router.get("/{bike_number}/location", response_model=bike_schemas.BikeLocation)
    def read_bike_location(self, bike_number: str):
        return self.service.get_current_location(bike_number)
