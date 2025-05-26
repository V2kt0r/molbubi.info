import numpy as np
from haversine import Unit, haversine_vector

from ..core.utils import group_bike_positions
from ..repositories.base import BikeRepository
from ..schemas.distance import DistanceResponse
from .base import DistanceService


class DistanceCalculatorService(DistanceService):
    def __init__(self, repository: BikeRepository):
        self.repository = repository

    async def get_all_distances(self) -> list[DistanceResponse]:
        bikes = await self.repository.get_all_bikes()
        positions = group_bike_positions(bikes)

        return sorted(
            [
                self._create_distance_response(bike_number, bike_group)
                for bike_number, bike_group in positions.items()
                if len(bike_group) >= 2
            ],
            key=lambda r: -r.total_distance,
        )

    async def get_bike_distance(self, bike_number: str) -> DistanceResponse | None:
        bikes = await self.repository.get_bikes_by_number(bike_number)
        if not bikes:
            return None

        return self._create_distance_response(bike_number, bikes)

    def _create_distance_response(
        self, bike_number: str, bike_group
    ) -> DistanceResponse:
        points = [(b.station.lat, b.station.lng) for b in bike_group if b.station]
        return DistanceResponse(
            bike_number=bike_number,
            total_distance=self._calculate_distance(points),
            travels=len(bike_group) - 1,
        )

    @staticmethod
    def _calculate_distance(points: list[tuple[float, float]]) -> float:
        if len(points) < 2:
            return 0.0

        start = np.array(points[:-1])
        end = np.array(points[1:])
        distances = haversine_vector(start, end, unit=Unit.KILOMETERS)
        return round(np.sum(distances), 2)
