from pydantic import BaseModel


class BikeSchema(BaseModel):
    number: str


class StationSchema(BaseModel):
    uid: int
    lat: float
    lng: float
    name: str
    spot: bool
    bike_list: list[BikeSchema]


class CitySchema(BaseModel):
    places: list[StationSchema]


class CountrySchema(BaseModel):
    cities: list[CitySchema]


class ApiResponse(BaseModel):
    countries: list[CountrySchema]
