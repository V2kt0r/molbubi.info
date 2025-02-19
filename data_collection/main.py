import os
import time
from datetime import UTC, datetime

import requests
import schedule
from shared.database import Session
from shared.logger import logger
from shared.models import BikeModel, StationModel
from sqlalchemy.orm import Session as SessionType

from .cache_service import CacheService
from .schemas import ApiResponse, BikeSchema, StationSchema

API_URL = os.getenv("API_URL")


cache_service = CacheService()
cache_service.fetch()


def extract_relevant_data(raw_data: dict) -> list[StationSchema]:
    # I only query data for Budapest
    # The response will only have 1 country (Hungary)
    # And 1 city (Budapest)
    data = ApiResponse.model_validate(raw_data)
    return data.countries[0].cities[0].places


def fetch_stations() -> list[StationSchema]:
    response = requests.get(API_URL)
    response.raise_for_status()
    stations = extract_relevant_data(response.json())
    logger.debug(f"Retrieved data for {len(stations)} stations from API")

    return stations


def add_new_station(session: SessionType, station: StationSchema):
    new_station = StationModel(
        uid=station.uid, name=station.name, lat=station.lat, lng=station.lng
    )
    session.add(new_station)

    cache_service.station_uids.add(station.uid)

    logger.info(f"Added new station: {station.uid}")


def add_new_bike(
    session: SessionType,
    bike: BikeSchema,
    station: StationSchema,
    current_time: datetime,
):
    new_bike = BikeModel(
        number=bike.number, timestamp=current_time, station_uid=station.uid
    )
    session.add(new_bike)

    cache_service.bike_station[bike.number] = station.uid

    logger.info(f"Bike {bike.number} moved to {station.uid}")


def process_bikes(session: SessionType, station: StationSchema):
    current_time = datetime.now(UTC)
    for bike in station.bike_list:
        if cache_service.has_bike_moved(bike, station):
            add_new_bike(session, bike, station, current_time)


def process_stations(session: SessionType, stations: list[StationSchema]):
    for station in stations:
        # Bikes outside stations are included in the places list.
        # The "spot" attribute for these are false
        # We don't need these
        if station.spot == False:
            continue

        # Create new station if it doesn't exist
        if station.uid not in cache_service.station_uids:
            add_new_station(session, station)

        # Save bikes
        process_bikes(session, station)


def query_api_and_save():
    try:
        logger.debug("Starting API query and data save process")

        session = Session()

        stations = fetch_stations()
        process_stations(session, stations)

        session.commit()
        logger.debug("Data saved successfully")
    except Exception as e:
        logger.error(f"Error in query_api_and_save: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()


def main():
    logger.info("Starting data collection service")
    schedule.every(10).seconds.do(query_api_and_save)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
