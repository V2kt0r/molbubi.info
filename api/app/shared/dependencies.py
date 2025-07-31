from fastapi import Depends
from sqlalchemy.orm import Session

from app.shared.database import get_db

# Repository imports
from app.bikes.repository import BikeRepository
from app.stations.repository import BikeStayRepository, RedisRepository, StationRepository
from app.distribution.repository import DistributionRepository

# Service imports
from app.bikes.service import BikeService
from app.stations.service import StationService
from app.distribution.service import DistributionService


# Repository Providers
def get_station_repo(db: Session = Depends(get_db)) -> StationRepository:
    return StationRepository(db)


def get_bike_repo(db: Session = Depends(get_db)) -> BikeRepository:
    return BikeRepository(db)


def get_redis_repo() -> RedisRepository:
    return RedisRepository()


def get_bike_stay_repo(db: Session = Depends(get_db)) -> BikeStayRepository:
    return BikeStayRepository(db)


def get_distribution_repo(db: Session = Depends(get_db)) -> DistributionRepository:
    return DistributionRepository(db)


# Service Providers
def get_station_service(
    station_repo: StationRepository = Depends(get_station_repo),
    redis_repo: RedisRepository = Depends(get_redis_repo),
    stay_repo: BikeStayRepository = Depends(get_bike_stay_repo),
) -> StationService:
    return StationService(station_repo, redis_repo, stay_repo)


def get_bike_service(
    bike_repo: BikeRepository = Depends(get_bike_repo),
    station_repo: StationRepository = Depends(get_station_repo),
) -> BikeService:
    return BikeService(bike_repo, station_repo)


def get_distribution_service(
    distribution_repo: DistributionRepository = Depends(get_distribution_repo),
) -> DistributionService:
    return DistributionService(distribution_repo)