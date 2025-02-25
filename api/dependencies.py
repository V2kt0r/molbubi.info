from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from shared.logger import logger

from .repositories.bike_repository import BikeRepository
from .services.bike_service import BikeService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Session error: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


def get_bike_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> BikeRepository:
    return BikeRepository(session)


def get_bike_service(
    repository: Annotated[BikeRepository, Depends(get_bike_repository)]
) -> BikeService:
    return BikeService(repository)


BikeServiceDep = Annotated[BikeService, Depends(get_bike_service)]
