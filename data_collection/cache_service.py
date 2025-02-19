from shared.database import Session
from shared.logger import logger
from shared.models import BikeModel, StationModel
from sqlalchemy import func, select

from .schemas import BikeSchema, StationSchema


class CacheService:
    def fetch(self):
        try:
            session = Session()
            stations = session.execute(select(StationModel)).scalars()

            # Get latest data for each bike
            latest_timestamp = (
                session.query(
                    BikeModel.number,
                    func.max(BikeModel.timestamp).label("max_timestamp"),
                )
                .group_by(BikeModel.number)
                .subquery()
            )

            bikes = (
                session.query(BikeModel)
                .join(
                    latest_timestamp,
                    (BikeModel.number == latest_timestamp.c.number)
                    & (BikeModel.timestamp == latest_timestamp.c.max_timestamp),
                )
                .all()
            )

            self.station_uids = set(station.uid for station in stations)
            self.bike_station: dict[str, int] = {
                bike.number: bike.station_uid for bike in bikes
            }
        except Exception as e:
            logger.error(f"Error in CacheService.fetch: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def has_bike_moved(self, bike: BikeSchema, new_station: StationSchema) -> bool:
        old_station_id = self.bike_station.get(bike.number)
        return old_station_id != new_station.uid
