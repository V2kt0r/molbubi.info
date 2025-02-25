from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import BikeModel, StationModel


class BikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_earliest_logs_subquery(self):
        return (
            select(
                BikeModel.number,
                func.min(BikeModel.timestamp).label("first_timestamp"),
            )
            .group_by(BikeModel.number)
            .subquery()
        )

    async def get_bike_history(self, bike_number: str):
        statement = (
            select(BikeModel, StationModel)
            .join(StationModel)
            .where(BikeModel.number == bike_number)
            .order_by(BikeModel.timestamp.desc())
        )
        result = await self.session.execute(statement)
        return result.all()

    async def get_all_bikes(self):
        statement = (
            select(BikeModel)
            .options(selectinload(BikeModel.station))
            .order_by(BikeModel.number, BikeModel.timestamp)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_bikes_by_number(self, bike_number: str):
        statement = (
            select(BikeModel)
            .options(selectinload(BikeModel.station))
            .where(BikeModel.number == bike_number)
            .order_by(BikeModel.timestamp)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_station_arrival_counts(self):
        earliest_logs = self._get_earliest_logs_subquery()

        statement = (
            select(StationModel, func.count(BikeModel.id).label("count"))
            .join(BikeModel, BikeModel.station_uid == StationModel.uid)
            .join(
                earliest_logs,
                and_(
                    BikeModel.number == earliest_logs.c.number,
                    BikeModel.timestamp > earliest_logs.c.first_timestamp,
                ),
            )
            .group_by(StationModel.uid)
            .order_by(func.count(BikeModel.id).desc())
        )
        result = await self.session.execute(statement)
        return result.all()

    async def get_arrival_count_by_hour(self):
        earliest_logs = self._get_earliest_logs_subquery()

        statement = (
            select(
                extract("hour", BikeModel.timestamp).label("hour"),
                func.count(BikeModel.id).label("count"),
            )
            .join(
                earliest_logs,
                (BikeModel.number == earliest_logs.c.number)
                & (BikeModel.timestamp > earliest_logs.c.first_timestamp),
            )
            .group_by(extract("hour", BikeModel.timestamp))
            .order_by(extract("hour", BikeModel.timestamp))
        )
        result = await self.session.execute(statement)
        return result.all()

    async def get_hour_and_station_arrival_counts(self):
        earliest_logs = self._get_earliest_logs_subquery()

        statement = (
            select(
                StationModel.name,
                StationModel.lat,
                StationModel.lng,
                extract("hour", BikeModel.timestamp).label("hour"),
                func.count(BikeModel.id).label("count"),
            )
            .join(BikeModel, BikeModel.station_uid == StationModel.uid)
            .join(
                earliest_logs,
                (BikeModel.number == earliest_logs.c.number)
                & (BikeModel.timestamp > earliest_logs.c.first_timestamp),
            )
            .group_by(StationModel.uid, extract("hour", BikeModel.timestamp))
            .order_by(
                extract("hour", BikeModel.timestamp), func.count(BikeModel.id).desc()
            )
        )
        result = await self.session.execute(statement)
        return result.all()
