from datetime import datetime

from pydantic import BaseModel


class BikeStay(BaseModel):
    """
    Represents a period of time a bike has spent at a single station.
    This schema is used for API responses.
    """
    bike_number: str
    station_uid: int
    start_time: datetime
    
    # The end_time can be None (null) if the stay is currently ongoing.
    end_time: datetime | None = None

    class Config:
        # This allows the Pydantic model to be created directly from
        # a SQLAlchemy ORM instance (e.g., your database model).
        from_attributes = True
