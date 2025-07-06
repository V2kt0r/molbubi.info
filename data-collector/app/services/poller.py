import logging

from pydantic import ValidationError

from app.api.client import ApiClient
from app.core.config import settings
from app.schemas.nextbike import ApiResponse
from app.storage.redis_client import RedisClient

logger = logging.getLogger(__name__)


class Poller:
    def __init__(
        self,
        api_client: ApiClient,
        redis_client: RedisClient,
        stream_name: str = settings.REDIS_STREAM_NAME,
    ):
        self.api_client = api_client
        self.redis_client = redis_client
        self.stream_name = stream_name

    def poll_and_store_data(self):
        logger.info("Starting data polling cycle...")
        raw_data = self.api_client.fetch_bike_data()
        if not raw_data:
            logger.warning("No data fetched. Skipping this cycle.")
            return

        try:
            validated_data = ApiResponse.model_validate(raw_data)
            logger.info("Data validation successful.")
        except ValidationError as e:
            logger.error(f"Data validation failed: {e}")
            return

        self.redis_client.add_to_stream(self.stream_name, validated_data.model_dump())
        logger.info("Data polling cycle finished successfully.")
