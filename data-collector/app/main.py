import asyncio
import logging

from app.api.client import ApiClient
from app.core.config import settings
from app.services.poller import Poller
from app.storage.redis_client import RedisClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main_loop(poller: Poller):
    logger.info("Data Collector service started.")
    logger.info(f"Polling interval: {settings.POLLING_INTERVAL_SECONDS} seconds.")
    logger.info(f"Storing data in Redis stream: '{settings.REDIS_STREAM_NAME}'")

    while True:
        try:
            poller.poll_and_store_data()
        except Exception as e:
            logger.critical(f"Unexpected error in polling loop: {e}", exc_info=True)
        await asyncio.sleep(settings.POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    api_client = ApiClient()
    redis_client = RedisClient()
    poller = Poller(api_client=api_client, redis_client=redis_client)

    try:
        asyncio.run(main_loop(poller))
    except KeyboardInterrupt:
        logger.info("Data Collector service stopped by user.")
