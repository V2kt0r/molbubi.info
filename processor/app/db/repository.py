from datetime import datetime

import redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.bike_data import BikeState
from app.schemas.bike_data import Station as StationSchema

from shared_models.models import Base, Station, BikeMovement, BikeStay


class BaseRepository:
    def __init__(self, db_session: Session):
        self.db = db_session


class StationRepository(BaseRepository):
    def get_by_uid(self, station_uid: int) -> Station | None:
        return (
            self.db.query(Station)
            .filter(Station.uid == station_uid)
            .first()
        )

    def upsert(self, station: StationSchema) -> Station:
        db_station = self.get_by_uid(station.uid)
        if not db_station:
            db_station = Station(**station.model_dump(exclude={"spot", "bike_list"}))
            self.db.add(db_station)
        else:
            db_station.name = station.name
            db_station.lat = station.lat
            db_station.lng = station.lng

        self.db.commit()
        self.db.refresh(db_station)
        return db_station


class BikeMovementRepository(BaseRepository):
    def create(self, movement_data: dict) -> BikeMovement:
        db_movement = BikeMovement(**movement_data)
        self.db.add(db_movement)
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement


class RedisRepository:
    def __init__(
        self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_DOCKER_PORT
    ):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.bike_state_hash = settings.REDIS_BIKE_STATE_HASH
        self.station_bikes_prefix = settings.REDIS_STATION_BIKES_SET_PREFIX

    def get_bike_state(self, bike_number: str) -> BikeState | None:
        state_json = self.client.hget(self.bike_state_hash, bike_number)
        if not state_json:
            return None
        
        try:
            return BikeState.model_validate_json(state_json)
        except Exception:
            # Handle invalid JSON or validation errors gracefully
            return None

    def set_bike_state(self, bike_number: str, state_data: dict):
        state = BikeState(**state_data)
        self.client.hset(self.bike_state_hash, bike_number, state.model_dump_json())

    def update_station_occupancy(self, station_uid: int, bike_numbers: set[str]):
        station_key = f"{self.station_bikes_prefix}:{station_uid}"
        pipeline = self.client.pipeline()
        pipeline.delete(station_key)
        if bike_numbers:
            pipeline.sadd(station_key, *bike_numbers)
        pipeline.execute()


class BikeStayRepository(BaseRepository):
    def find_active_stay(self, bike_number: str):
        """Finds the current stay for a bike (where end_time is NULL)."""
        return self.db.query(BikeStay).filter(
            BikeStay.bike_number == bike_number,
            BikeStay.end_time == None
        ).first()

    def create_stay(self, stay_data: dict):
        """Creates a new stay record."""
        db_stay = BikeStay(**stay_data)
        self.db.add(db_stay)
        self.db.commit()
        return db_stay

    def end_stay(self, stay: BikeStay, end_time: datetime):
        """Updates the end_time of an existing stay."""
        stay.end_time = end_time
        self.db.commit()
