import logging
import math
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.repository import (
    BikeMovementRepository,
    BikeStayRepository,
    RedisRepository,
    StationRepository,
)
from app.schemas.bike_data import ApiResponse

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, db: Session, redis_repo: RedisRepository):
        self.station_repo = StationRepository(db)
        self.movement_repo = BikeMovementRepository(db)
        self.stay_repo = BikeStayRepository(db)
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

    def _detect_and_record_movement(self, bike_number: str, current_station_uid: int, current_timestamp: float):
        last_state = self.redis_repo.get_bike_state(bike_number)
        
        # --- Stay Management Logic ---
        active_stay = self.stay_repo.find_active_stay(bike_number)
        
        if last_state:
            # If the bike moved, end the previous stay
            if last_state.station_uid != current_station_uid:
                if active_stay:
                    # The end time of the stay is the start time of the movement
                    self.stay_repo.end_stay(active_stay, datetime.fromtimestamp(last_state.timestamp, tz=timezone.utc))
                
                # A new stay begins now at the new station
                new_stay_start_time = current_timestamp
                self.stay_repo.create_stay({
                    "bike_number": bike_number,
                    "station_uid": current_station_uid,
                    "start_time": datetime.fromtimestamp(new_stay_start_time, tz=timezone.utc)
                })
            else:
                # Bike is at the same station, continue the stay
                new_stay_start_time = last_state.stay_start_time or last_state.timestamp
        else:
            # Bike is seen for the first time, start a new stay
            new_stay_start_time = current_timestamp
            self.stay_repo.create_stay({
                "bike_number": bike_number,
                "station_uid": current_station_uid,
                "start_time": datetime.fromtimestamp(new_stay_start_time, tz=timezone.utc)
            })

        # --- Movement and State Update Logic (includes movement creation) ---
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

        self.redis_repo.set_bike_state(bike_number, {
            "station_uid": current_station_uid, 
            "timestamp": current_timestamp,
            "stay_start_time": new_stay_start_time # Persist the stay start time
        })

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
