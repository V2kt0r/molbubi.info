import logging
import math
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.repository import BikeMovementRepository, RedisRepository, StationRepository
from app.schemas.bike_data import ApiResponse

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, db: Session, redis_repo: RedisRepository):
        self.station_repo = StationRepository(db)
        self.movement_repo = BikeMovementRepository(db)
        self.redis_repo = redis_repo

    def process_snapshot(self, snapshot: ApiResponse):
        processing_time = time.time()
        for country in snapshot.countries:
            for city in country.cities:
                for station in city.places:
                    if not station.spot:
                        continue

                    self.station_repo.upsert(station)

                    current_bike_numbers = {bike.number for bike in station.bike_list}
                    self.redis_repo.update_station_occupancy(
                        station.uid, current_bike_numbers
                    )

                    for bike in station.bike_list:
                        self._detect_and_record_movement(
                            bike.number, station.uid, processing_time
                        )

    def _detect_and_record_movement(
        self, bike_number: str, current_station_uid: int, current_timestamp: float
    ):
        last_state = self.redis_repo.get_bike_state(bike_number)

        if last_state and last_state.station_uid != current_station_uid:
            logger.info(
                f"Movement detected for bike {bike_number}: {last_state.station_uid} -> {current_station_uid}"
            )

            start_station = self.station_repo.get_by_uid(last_state.station_uid)
            end_station = self.station_repo.get_by_uid(current_station_uid)

            distance = 0.0
            if start_station and end_station:
                distance = self._haversine_distance(
                    start_station.lat,
                    start_station.lng,
                    end_station.lat,
                    end_station.lng,
                )

            self.movement_repo.create(
                {
                    "bike_number": bike_number,
                    "start_station_uid": last_state.station_uid,
                    "end_station_uid": current_station_uid,
                    "start_time": datetime.fromtimestamp(
                        last_state.timestamp, tz=timezone.utc
                    ),
                    "end_time": datetime.fromtimestamp(
                        current_timestamp, tz=timezone.utc
                    ),
                    "distance_km": distance,
                }
            )

        self.redis_repo.set_bike_state(
            bike_number,
            {"station_uid": current_station_uid, "timestamp": current_timestamp},
        )

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (
            math.sin(dLat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dLon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
