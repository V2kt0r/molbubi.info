from datetime import time

from ..repositories.base import BikeRepository
from ..schemas.distribution import (
    ArrivalCountByHourResponse,
    HourAndStationArrivalCountResponse,
    StationArrivalCountResponse,
)
from .base import DistributionService


class DistributionAnalysisService(DistributionService):
    def __init__(self, repository: BikeRepository):
        self.repository = repository

    async def get_all_station_distribution(self) -> list[StationArrivalCountResponse]:
        station_counts = await self.repository.get_station_arrival_counts()
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

    async def get_distribution_by_hour(self) -> list[ArrivalCountByHourResponse]:
        hourly_counts = await self.repository.get_arrival_count_by_hour()
        return [
            ArrivalCountByHourResponse(
                time=time(hour=int(hour)),
                arrival_count=count,
            )
            for hour, count in hourly_counts
        ]

    async def get_hour_and_station_distribution(
        self,
    ) -> list[HourAndStationArrivalCountResponse]:
        station_hour_counts = (
            await self.repository.get_hour_and_station_arrival_counts()
        )
        return [
            HourAndStationArrivalCountResponse(
                time=time(hour=int(hour)),
                station_name=station_name,
                latitude=latitude,
                longitude=longitude,
                arrival_count=count,
            )
            for station_name, latitude, longitude, hour, count in station_hour_counts
        ]
