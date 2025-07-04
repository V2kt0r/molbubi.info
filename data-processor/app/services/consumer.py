import redis
import json
import logging
import time
from datetime import datetime, timezone
from pydantic import ValidationError
import math

from app.core.config import settings
from app.db import crud, database, models
from app.schemas.bike_data import ApiResponse, BikeState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in kilometers."""
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class DataConsumer:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )
        self.db_session_gen = database.get_db
        self.ensure_consumer_group()

    def ensure_consumer_group(self):
        """Creates the Redis consumer group if it doesn't exist."""
        try:
            self.redis_client.xgroup_create(
                name=settings.REDIS_STREAM_NAME,
                groupname=settings.REDIS_CONSUMER_GROUP,
                id="0",
                mkstream=True,
            )
            logger.info(f"Consumer group '{settings.REDIS_CONSUMER_GROUP}' created.")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(
                    f"Consumer group '{settings.REDIS_CONSUMER_GROUP}' already exists."
                )
            else:
                raise

    def process_messages(self):
        """Main loop to read from stream and process data."""
        logger.info("Starting to listen for messages...")
        while True:
            try:
                # Read from the stream, block for up to 2 seconds if no messages
                messages = self.redis_client.xreadgroup(
                    groupname=settings.REDIS_CONSUMER_GROUP,
                    consumername=settings.REDIS_CONSUMER_NAME,
                    streams={settings.REDIS_STREAM_NAME: ">"},
                    count=1,
                    block=2000,
                )
                if not messages:
                    continue

                for stream, msg_list in messages:
                    for msg_id, data in msg_list:
                        self.handle_message(msg_id, data)
            except Exception as e:
                logger.error(f"Error while processing messages: {e}", exc_info=True)
                time.sleep(5)  # Wait before retrying

    def handle_message(self, msg_id: str, data: dict):
        """Process a single message from the stream."""
        try:
            snapshot_data = json.loads(data["data"])
            validated_snapshot = ApiResponse.model_validate(snapshot_data)
            processing_time = time.time()

            db = next(self.db_session_gen())

            # Store all bikes found in this snapshot to determine which are now gone
            all_bikes_in_snapshot = set()

            for country in validated_snapshot.countries:
                for city in country.cities:
                    # We will update station bikes in a single transaction
                    redis_pipeline = self.redis_client.pipeline()

                    for station in city.places:
                        if not station.spot:
                            continue

                        crud.upsert_station(db, station)

                        station_key = (
                            f"{settings.REDIS_STATION_BIKES_SET_PREFIX}{station.uid}"
                        )

                        current_bike_numbers = {
                            bike.number for bike in station.bike_list
                        }

                        redis_pipeline.delete(station_key)
                        if current_bike_numbers:
                            redis_pipeline.sadd(station_key, *current_bike_numbers)

                        for bike in station.bike_list:
                            all_bikes_in_snapshot.add(bike.number)
                            self.detect_movement(
                                db, bike.number, station.uid, processing_time
                            )

                    redis_pipeline.execute()
                    logger.info("Updated real-time station bike occupancy in Redis.")

            self.redis_client.xack(
                settings.REDIS_STREAM_NAME, settings.REDIS_CONSUMER_GROUP, msg_id
            )
            logger.info(f"Successfully processed and acknowledged message {msg_id}")

        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(
                f"Validation/JSON error for message {msg_id}: {e}. Acknowledging to avoid reprocessing."
            )
            self.redis_client.xack(
                settings.REDIS_STREAM_NAME, settings.REDIS_CONSUMER_GROUP, msg_id
            )
        except Exception as e:
            logger.error(
                f"Failed to process message {msg_id}: {e}. It will be retried."
            )
        finally:
            if "db" in locals():
                db.close()

    def detect_movement(
        self, db, bike_number: str, current_station_uid: int, current_timestamp: float
    ):
        """Compares current bike state with previous to detect movement."""
        state_key = settings.REDIS_BIKE_STATE_HASH
        previous_state_json = self.redis_client.hget(state_key, bike_number)

        if previous_state_json:
            last_state = BikeState.model_validate(json.loads(previous_state_json))

            if last_state.station_uid != current_station_uid:
                logger.info(
                    f"Movement detected for bike {bike_number}: from {last_state.station_uid} to {current_station_uid}"
                )

                # Fetch station coordinates to calculate distance
                start_station = (
                    db.query(models.Station)
                    .filter(models.Station.uid == last_state.station_uid)
                    .first()
                )
                end_station = (
                    db.query(models.Station)
                    .filter(models.Station.uid == current_station_uid)
                    .first()
                )

                distance = 0.0
                if start_station and end_station:
                    distance = haversine_distance(
                        start_station.lat,
                        start_station.lng,
                        end_station.lat,
                        end_station.lng,
                    )

                crud.create_bike_movement(
                    db=db,
                    bike_number=bike_number,
                    start_station_uid=last_state.station_uid,
                    end_station_uid=current_station_uid,
                    start_time=datetime.fromtimestamp(
                        last_state.timestamp, tz=timezone.utc
                    ),
                    end_time=datetime.fromtimestamp(current_timestamp, tz=timezone.utc),
                    distance_km=distance,
                )

        new_state = BikeState(
            station_uid=current_station_uid, timestamp=current_timestamp
        )
        self.redis_client.hset(state_key, bike_number, new_state.model_dump_json())
