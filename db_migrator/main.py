import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine

from shared.logger import setup_logger
from shared.models import Base

logger = setup_logger("db_migrator", "db_migrator.log")

DATABASE_URL = os.getenv("DATABASE_URL")


async def run_migrations():
    logger.info("Starting database migrations")
    engine = create_async_engine(DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            logger.info("Creating database schema")
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error during database migration: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migrations())
