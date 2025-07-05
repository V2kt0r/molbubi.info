from fastapi import APIRouter

from .endpoints.bikes import router as bikes_router
from .endpoints.stations import router as stations_router

api_router = APIRouter()

api_router.include_router(stations_router, prefix="/stations", tags=["Stations"])
api_router.include_router(bikes_router, prefix="/bikes", tags=["Bikes"])
