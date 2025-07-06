import json
import logging

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_PORT):
        try:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
            self.client.ping()
            logger.info("Connected to Redis successfully.")
        except redis.ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            raise

    def add_to_stream(self, stream_name: str, data: dict):
        try:
            payload = {'data': json.dumps(data)}
            self.client.xadd(stream_name, payload)
            logger.info(f"Added data to stream '{stream_name}'")
        except Exception as e:
            logger.error(f"Error adding data to Redis stream: {e}")
