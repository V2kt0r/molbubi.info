from datetime import time

from pydantic import BaseModel


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
