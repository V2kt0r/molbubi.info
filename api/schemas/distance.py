from pydantic import BaseModel


class DistanceResponse(BaseModel):
    bike_number: str
    total_distance: float
    distance_unit: str = "km"
    travels: int
