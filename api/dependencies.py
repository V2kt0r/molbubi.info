from typing import Annotated, Generator

from fastapi import Depends
from shared.database import Session
from shared.logger import logger
from sqlalchemy.orm import Session as SessionType

from .repositories.bike_repository import BikeRepository
from .services.bike_service import BikeService


def get_session() -> Generator[SessionType, any, any]:
    try:
        session = Session()
        yield session
    except Exception as e:
        logger.error(f"Error during session dependency: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()


SessionDep = Annotated[SessionType, Depends(get_session)]


def get_bike_repository(session: SessionDep) -> BikeRepository:
    return BikeRepository(session)


def get_bike_service(
    repository: Annotated[BikeRepository, Depends(get_bike_repository)]
) -> BikeService:
    return BikeService(repository)


BikeServiceDep = Annotated[BikeService, Depends(get_bike_service)]
