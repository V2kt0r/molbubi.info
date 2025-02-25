from typing import Annotated

from fastapi import Depends

from ...repositories.bike_repository import SQLAlchemyBikeRepository
from .session import SessionDep


def get_bike_repository(session: SessionDep) -> SQLAlchemyBikeRepository:
    return SQLAlchemyBikeRepository(session)


BikeRepositoryDep = Annotated[SQLAlchemyBikeRepository, Depends(get_bike_repository)]
