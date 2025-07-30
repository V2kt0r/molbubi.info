from pydantic import BaseModel


class StationBase(BaseModel):
    uid: int
    name: str
    lat: float
    lng: float


class Station(StationBase):
    class Config:
        from_attributes = True


class StationStats(BaseModel):
    total_arrivals: int
    total_departures: int
