from abc import ABC, abstractmethod

from ..schemas.distance import DistanceResponse
from ..schemas.distribution import (
    ArrivalCountByHourResponse,
    HourAndStationArrivalCountResponse,
    StationArrivalCountResponse,
)
from ..schemas.history import HistoryResponse


class DistanceService(ABC):
    @abstractmethod
    async def get_all_distances(self) -> list[DistanceResponse]: ...

    @abstractmethod
    async def get_bike_distance(self, bike_number: str) -> DistanceResponse | None: ...


class HistoryService(ABC):
    @abstractmethod
    async def get_bike_history(self, bike_number: str) -> HistoryResponse | None: ...


class DistributionService(ABC):
    @abstractmethod
    async def get_all_station_distribution(
        self,
    ) -> list[StationArrivalCountResponse]: ...

    @abstractmethod
    async def get_distribution_by_hour(self) -> list[ArrivalCountByHourResponse]: ...

    @abstractmethod
    async def get_hour_and_station_distribution(
        self,
    ) -> list[HourAndStationArrivalCountResponse]: ...
