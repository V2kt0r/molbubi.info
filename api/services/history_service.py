from ..repositories.base import BikeRepository
from ..schemas.history import HistoryElement, HistoryResponse
from .base import HistoryService


class HistoryQueryService(HistoryService):
    def __init__(self, repository: BikeRepository):
        self.repository = repository

    async def get_bike_history(self, bike_number: str) -> HistoryResponse | None:
        result = await self.repository.get_bike_history(bike_number)
        if not result:
            return None

        return HistoryResponse(
            bike_number=bike_number,
            history=[
                HistoryElement(
                    station_name=station.name,
                    latitude=station.lat,
                    longitude=station.lng,
                    timestamp=bike.timestamp,
                )
                for bike, station in result
            ],
        )
