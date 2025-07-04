import logging
from pydantic import ValidationError

from app.api import client as api_client
from app.storage import redis_client
from app.schemas.nextbike import ApiResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def poll_and_store_data():
    """
    Orchestrates one cycle of fetching, validating, and storing data.
    """
    logger.info("Starting data polling cycle...")

    raw_data = api_client.fetch_bike_data()
    if not raw_data:
        logger.warning("No data fetched. Skipping this cycle.")
        return

    try:
        validated_data = ApiResponse.model_validate(raw_data)
        logger.info("Data validation successful.")
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        return

    redis_client.store_data(validated_data)
    logger.info("Data polling cycle finished successfully.")
