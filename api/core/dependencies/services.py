from typing import Annotated

from fastapi import Depends

from ...services.base import DistanceService, DistributionService, HistoryService
from ...services.bike_service_provider import BikeServiceProvider
from .repositories import BikeRepositoryDep


def get_distance_service(repository: BikeRepositoryDep) -> DistanceService:
    return BikeServiceProvider.get_distance_service(repository)


DistanceServiceDep = Annotated[DistanceService, Depends(get_distance_service)]


def get_history_service(repository: BikeRepositoryDep) -> HistoryService:
    return BikeServiceProvider.get_history_service(repository)


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]


def get_distribution_service(repository: BikeRepositoryDep) -> DistributionService:
    return BikeServiceProvider.get_distribution_service(repository)


DistributionServiceDep = Annotated[
    DistributionService, Depends(get_distribution_service)
]
