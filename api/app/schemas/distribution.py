from pydantic import BaseModel


class HourlyDistribution(BaseModel):
    time: int  # Hour (0-23)
    arrival_count: int
    
    class Config:
        from_attributes = True