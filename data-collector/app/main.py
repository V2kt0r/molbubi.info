import asyncio
import logging
from app.core.config import settings
from app.services.poller import poll_and_store_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main_loop():
    """
    Main execution loop that runs the polling task periodically.
    """
    logger.info("Data Collector service started.")
    logger.info(f"Polling interval: {settings.POLLING_INTERVAL_SECONDS} seconds.")
    logger.info(f"Storing data in Redis stream: '{settings.REDIS_STREAM_NAME}'")

    while True:
        try:
            poll_and_store_data()
        except Exception as e:
            # Catching broad exceptions here to ensure the loop continues
            # even if a critical error occurs in one cycle (e.g., Redis down).
            logger.critical(
                f"An unexpected error occurred in the main loop: {e}", exc_info=True
            )

        await asyncio.sleep(settings.POLLING_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Data Collector service stopped by user.")
