from itertools import groupby

import numpy as np
from haversine import Unit, haversine_vector

from ..repositories.bike_repository import BikeRepository
from ..schemas import (
    DistanceResponse,
    HistoryElement,
    HistoryResponse,
    StationArrivalCountResponse,
)


class BikeService:
    def __init__(self, repository: BikeRepository):
        self.repository = repository

    def get_bike_history(self, bike_number: str) -> HistoryResponse | None:
        result = self.repository.get_bike_history(bike_number)

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

    @staticmethod
    def calculate_distance(points: list[tuple[float, float]]) -> float:
        if len(points) < 2:
            return 0.0

        start = np.array(points[:-1])
        end = np.array(points[1:])
        distances = haversine_vector(start, end, unit=Unit.KILOMETERS)

        return round(np.sum(distances), 2)

    def get_all_distances(self) -> list[DistanceResponse]:
        bikes = self.repository.get_all_bikes()
        positions = self._group_bike_positions(bikes)

        return sorted(
            [
                DistanceResponse(
                    bike_number=bike_number,
                    total_distance=self.calculate_distance(
                        [
                            (b.station.lat, b.station.lng)
                            for b in bike_group
                            if b.station
                        ]
                    ),
                    travels=len(bike_group) - 1,
                )
                for bike_number, bike_group in positions.items()
                if len(bike_group) >= 2
            ],
            key=lambda r: -r.total_distance,
        )

    def get_bike_distance(self, bike_number: str) -> DistanceResponse | None:
        bikes = self.repository.get_bikes_by_number(bike_number)
        if not bikes:
            return None

        points = [(b.station.lat, b.station.lng) for b in bikes]
        return DistanceResponse(
            bike_number=bike_number,
            total_distance=self.calculate_distance(points),
            travels=len(points) - 1,
        )

    def get_all_station_distribution(self) -> list[StationArrivalCountResponse]:
        station_counts = self.repository.get_station_arrival_counts()

        return sorted(
            [
                StationArrivalCountResponse(
                    station_name=station.name,
                    latitude=station.lat,
                    longitude=station.lng,
                    arrival_count=count,
                )
                for station, count in station_counts
            ],
            key=lambda r: -r.arrival_count,
        )

    def _group_bike_positions(self, bikes):
        return {
            num: list(group)
            for num, group in groupby(
                sorted(bikes, key=lambda b: b.number), key=lambda b: b.number
            )
        }
