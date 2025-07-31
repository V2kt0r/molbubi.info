from pydantic import BaseModel


class HourlyArrivalDistribution(BaseModel):
    time: int  # Hour (0-23)
    arrival_count: int
    
    class Config:
        from_attributes = True


class HourlyDepartureDistribution(BaseModel):
    time: int  # Hour (0-23)
    departure_count: int
    
    class Config:
        from_attributes = True