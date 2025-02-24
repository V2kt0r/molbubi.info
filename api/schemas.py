from datetime import datetime, time

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
    distance_unit: str = "km"
    travels: int


class StationArrivalCountResponse(BaseModel):
    station_name: str
    latitude: float
    longitude: float
    arrival_count: int


class ArrivalCountByHourResponse(BaseModel):
    time: time
    arrival_count: int


class HourAndStationArrivalCountResponse(BaseModel):
    time: time
    station_name: str
    latitude: float
    longitude: float
    arrival_count: int
