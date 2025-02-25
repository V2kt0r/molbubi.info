from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class BikeRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_bike_history(self, bike_number: str): ...

    @abstractmethod
    async def get_all_bikes(self): ...

    @abstractmethod
    async def get_bikes_by_number(self, bike_number: str): ...

    @abstractmethod
    async def get_station_arrival_counts(self): ...

    @abstractmethod
    async def get_arrival_count_by_hour(self): ...

    @abstractmethod
    async def get_hour_and_station_arrival_counts(self): ...
