from fastapi import APIRouter
from .endpoints import stations, bikes

api_router = APIRouter()
api_router.include_router(stations.router, prefix="/stations", tags=["Stations"])
api_router.include_router(bikes.router, prefix="/bikes", tags=["Bikes"])
