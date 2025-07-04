import redis
import json
import logging
from app.core.config import settings
from app.schemas.nextbike import ApiResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, host: str, port: int):
        try:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
            self.client.ping()
            logger.info("Successfully connected to Redis.")
        except redis.ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            raise

    def add_to_stream(self, stream_name: str, data: dict):
        """
        Adds a data entry to a Redis Stream.
        The data is serialized to JSON.
        """
        try:
            # Redis streams store data as a dictionary of string key-value pairs.
            # We'll serialize the entire pydantic model into a JSON string under one key.
            payload = {"data": json.dumps(data)}
            self.client.xadd(stream_name, payload)
            logger.info(f"Added data to stream '{stream_name}'")
        except Exception as e:
            logger.error(f"Error adding data to Redis stream: {e}")


# Singleton instance
redis_client = RedisClient(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def store_data(validated_data: ApiResponse):
    """
    Stores the validated data in a Redis stream.
    """
    # Convert Pydantic model to dict for JSON serialization
    data_dict = validated_data.model_dump()
    redis_client.add_to_stream(settings.REDIS_STREAM_NAME, data_dict)
