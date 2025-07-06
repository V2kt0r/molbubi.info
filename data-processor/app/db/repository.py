import redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.bike_data import BikeState
from app.schemas.bike_data import Station as StationSchema

from . import models


class BaseRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

class StationRepository(BaseRepository):
    def get_by_uid(self, station_uid: int) -> models.Station | None:
        return self.db.query(models.Station).filter(models.Station.uid == station_uid).first()

    def upsert(self, station: StationSchema) -> models.Station:
        db_station = self.get_by_uid(station.uid)
        if not db_station:
            db_station = models.Station(**station.model_dump())
            self.db.add(db_station)
        else:
            db_station.name = station.name
            db_station.lat = station.lat
            db_station.lng = station.lng
        
        self.db.commit()
        self.db.refresh(db_station)
        return db_station

class BikeMovementRepository(BaseRepository):
    def create(self, movement_data: dict) -> models.BikeMovement:
        db_movement = models.BikeMovement(**movement_data)
        self.db.add(db_movement)
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement

class RedisRepository:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_PORT):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.bike_state_hash = settings.REDIS_BIKE_STATE_HASH
        self.station_bikes_prefix = "station_bikes:"

    def get_bike_state(self, bike_number: str) -> BikeState | None:
        state_json = self.client.hget(self.bike_state_hash, bike_number)
        return BikeState.model_validate_json(state_json) if state_json else None

    def set_bike_state(self, bike_number: str, state_data: dict):
        state = BikeState(**state_data)
        self.client.hset(self.bike_state_hash, bike_number, state.model_dump_json())

    def update_station_occupancy(self, station_uid: int, bike_numbers: set[str]):
        station_key = f"{self.station_bikes_prefix}{station_uid}"
        pipeline = self.client.pipeline()
        pipeline.delete(station_key)
        if bike_numbers:
            pipeline.sadd(station_key, *bike_numbers)
        pipeline.execute()
