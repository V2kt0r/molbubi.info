import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .logger import setup_logger

logger = setup_logger("database", "database.log")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)


async def wait_for_db(max_retries=5, retry_interval=2):
    """Wait for database to be ready and accessible"""
    for attempt in range(max_retries):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.warning(
                f"Database connection attempt {attempt+1}/{max_retries} failed: {e}"
            )
            await asyncio.sleep(retry_interval)

    logger.error(f"Could not connect to database after {max_retries} attempts")
    return False


AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
