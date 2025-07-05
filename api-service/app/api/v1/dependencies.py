from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import BikeRepository, RedisRepository, StationRepository
from app.services.bike_service import BikeService
from app.services.station_service import StationService


# Repository Providers
def get_station_repo(db: Session = Depends(get_db)) -> StationRepository:
    return StationRepository(db)

def get_bike_repo(db: Session = Depends(get_db)) -> BikeRepository:
    return BikeRepository(db)

def get_redis_repo() -> RedisRepository:
    return RedisRepository()

# Service Providers
def get_station_service(
    station_repo: StationRepository = Depends(get_station_repo),
    redis_repo: RedisRepository = Depends(get_redis_repo)
) -> StationService:
    return StationService(station_repo, redis_repo)

def get_bike_service(
    bike_repo: BikeRepository = Depends(get_bike_repo),
    station_repo: StationRepository = Depends(get_station_repo)
) -> BikeService:
    return BikeService(bike_repo, station_repo)
