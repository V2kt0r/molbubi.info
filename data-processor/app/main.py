import logging
from app.db.database import init_db
from app.services.consumer import DataConsumer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Data Processor service...")

    # Initialize DB (create tables and hypertable if they don't exist)
    init_db()

    # Start the consumer
    consumer = DataConsumer()
    consumer.process_messages()


if __name__ == "__main__":
    main()
