from pydantic import BaseModel, Field


class Bike(BaseModel):
    number: str


class Station(BaseModel):
    uid: int
    lat: float
    lng: float
    name: str
    spot: bool
    bike_list: list[Bike] = Field(default_factory=list)


class City(BaseModel):
    places: list[Station] = Field(default_factory=list)


class Country(BaseModel):
    cities: list[City] = Field(default_factory=list)


class ApiResponse(BaseModel):
    countries: list[Country] = Field(default_factory=list)
