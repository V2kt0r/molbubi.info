from datetime import datetime

from pydantic import BaseModel


class HistoryElement(BaseModel):
    station_name: str
    latitude: float
    longitude: float
    timestamp: datetime


class HistoryResponse(BaseModel):
    bike_number: str
    history: list[HistoryElement]


class DistanceResponse(BaseModel):
    bike_number: str
    total_distance: float
    travels: int
    distance_unit: str = "km"
