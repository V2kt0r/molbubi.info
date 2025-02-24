from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from shared.models import BikeModel, StationModel


class BikeRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_bike_history(self, bike_number: str):
        statement = (
            select(BikeModel, StationModel)
            .join(StationModel)
            .where(BikeModel.number == bike_number)
            .order_by(BikeModel.timestamp.desc())
        )
        return self.session.execute(statement).all()

    def get_all_bikes(self):
        return (
            self.session.query(BikeModel)
            .order_by(BikeModel.number, BikeModel.timestamp)
            .all()
        )

    def get_bikes_by_number(self, bike_number: str):
        return (
            self.session.query(BikeModel)
            .filter(BikeModel.number == bike_number)
            .order_by(BikeModel.timestamp)
            .all()
        )

    def get_station_arrival_counts(self):
        # Subquery to get the earliest timestamp for each bike
        earliest_logs = (
            self.session.query(
                BikeModel.number,
                func.min(BikeModel.timestamp).label("first_timestamp"),
            )
            .group_by(BikeModel.number)
            .subquery()
        )

        # Main query
        return (
            self.session.query(StationModel, func.count(BikeModel.id).label("count"))
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
            .all()
        )
