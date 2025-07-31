from pydantic import BaseModel
from datetime import datetime
from app.stations.schema import Station


class BikeMovement(BaseModel):
    bike_number: str
    start_station_uid: int
    end_station_uid: int
    start_time: datetime
    end_time: datetime
    distance_km: float | None = None

    class Config:
        from_attributes = True


class BikeLocation(BaseModel):
    bike_number: str
    last_seen: datetime
    current_station: Station


class BikeStats(BaseModel):
    bike_number: str
    total_trips: int
    total_distance_km: float


class BikeSummary(BikeStats):
    current_location: Station | None = None
