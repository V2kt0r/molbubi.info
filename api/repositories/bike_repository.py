from shared.models import BikeModel, StationModel
from sqlalchemy import select
from sqlalchemy.orm import Session


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
