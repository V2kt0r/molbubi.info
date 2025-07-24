import logging

import redis

from app.core.config import settings
from app.db.database import init_db
from app.services.consumer import DataConsumer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Data Processor service...")

    # Initialize the database (create tables and hypertable)
    init_db()

    # Initialize Redis client and start the consumer
    redis_client = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_DOCKER_PORT, decode_responses=True
    )
    consumer = DataConsumer(redis_client)
    consumer.run()


if __name__ == "__main__":
    main()
