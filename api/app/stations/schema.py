from pydantic import BaseModel


class StationBase(BaseModel):
    uid: int
    name: str
    lat: float
    lng: float


class Station(StationBase):
    class Config:
        from_attributes = True


class StationStats(StationBase):
    total_arrivals: int
    total_departures: int
    
    class Config:
        from_attributes = True


class StationBikeCount(StationBase):
    bike_count: int
    
    class Config:
        from_attributes = True
