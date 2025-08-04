from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi_restful.cbv import cbv

from app.bikes import schema as bike_schemas
from app.bikes.service import BikeService
from app.shared.dependencies import get_bike_service
from app.shared.schemas import PaginatedResponse

router = APIRouter()


@cbv(router)
class BikeCBV:
    service: BikeService = Depends(get_bike_service)

    @router.get("/", response_model=PaginatedResponse[bike_schemas.BikeSummary])
    def read_all_bikes_summary(self, skip: int = 0, limit: int = 100):
        return self.service.get_all_bikes_summary(skip, limit)

    @router.get(
        "/{bike_number}/history", response_model=PaginatedResponse[bike_schemas.BikeMovement]
    )
    def read_bike_history(
        self, 
        bike_number: str, 
        skip: int = 0, 
        limit: int = 25,
        days_back: int = Query(default=30, description="Number of days back to look for movements (improves performance)"),
        start_date: Optional[datetime] = Query(default=None, description="Start date filter (ISO format, overrides days_back)"),
        end_date: Optional[datetime] = Query(default=None, description="End date filter (ISO format)")
    ):
        """
        Get bike movement history with optional time filtering for better performance.
        
        - **days_back**: Limits search to recent N days (default: 30)
        - **start_date**: Explicit start date (overrides days_back if provided)  
        - **end_date**: Explicit end date filter (optional)
        
        Time filtering significantly improves query performance on large datasets.
        """
        return self.service.get_bike_history(bike_number, skip, limit, days_back, start_date, end_date)

    @router.get("/{bike_number}/location", response_model=bike_schemas.BikeLocation)
    def read_bike_location(self, bike_number: str):
        return self.service.get_current_location(bike_number)
