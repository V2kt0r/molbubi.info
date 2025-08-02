from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize TimescaleDB-specific features (tables are created by migrations)."""
    try:
        with engine.connect() as connection:
            # Enable the TimescaleDB extension
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))

            # Convert the movements table to a hypertable (if not already a hypertable)
            connection.execute(
                text(
                    "SELECT create_hypertable('bike_movements', 'start_time', if_not_exists => TRUE, migrate_data => true);"
                )
            )

            connection.execute(
                text(
                    "SELECT create_hypertable('bike_stays', 'start_time', if_not_exists => TRUE, migrate_data => true);"
                )
            )

            connection.commit()
        logger.info("TimescaleDB features initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize TimescaleDB features: {e}")
        raise
