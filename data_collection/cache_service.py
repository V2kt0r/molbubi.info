from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from shared.logger import setup_logger
from shared.models import BikeModel, StationModel

from .schemas import BikeSchema, StationSchema

logger = setup_logger("cache_service", "cache_service.log")


class CacheService:
    async def fetch(self):
        try:
            async with AsyncSessionLocal() as session:
                await self._fetch_data(session)
        except Exception as e:
            logger.error(f"Error in CacheService.fetch: {e}", exc_info=True)

    async def _fetch_data(self, session: AsyncSession):
        stations = await self._fetch_stations(session)
        bikes = await self._fetch_bikes(session)

        self.station_uids = set(station.uid for station in stations)
        self.bike_station = {bike.number: bike.station_uid for bike in bikes}

    async def _fetch_stations(self, session: AsyncSession) -> list[StationModel]:
        result = await session.execute(select(StationModel))
        return result.scalars().all()

    async def _fetch_bikes(self, session: AsyncSession) -> list[BikeModel]:
        latest_timestamp = (
            select(
                BikeModel.number, func.max(BikeModel.timestamp).label("max_timestamp")
            )
            .group_by(BikeModel.number)
            .subquery()
        )

        statement = select(BikeModel).join(
            latest_timestamp,
            (BikeModel.number == latest_timestamp.c.number)
            & (BikeModel.timestamp == latest_timestamp.c.max_timestamp),
        )

        result = await session.execute(statement)
        return result.scalars().all()

    def has_bike_moved(self, bike: BikeSchema, new_station: StationSchema) -> bool:
        old_station_id = self.bike_station.get(bike.number)
        return old_station_id != new_station.uid
