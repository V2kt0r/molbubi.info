from app.core.exceptions import BikeNotFound
from app.db.repository import BikeRepository, StationRepository
from app.schemas import bike as bike_schemas


class BikeService:
    def __init__(self, bike_repo: BikeRepository, station_repo: StationRepository):
        self.bike_repo = bike_repo
        self.station_repo = station_repo

    def get_bike_history(self, bike_number: str, skip: int, limit: int):
        return self.bike_repo.get_movements(bike_number, skip, limit)

    def get_current_location(self, bike_number: str):
        last_movement = self.bike_repo.get_latest_movement(bike_number)
        if not last_movement:
            raise BikeNotFound(bike_number)
        
        station = self.station_repo.get_by_uid(last_movement.end_station_uid)
        return bike_schemas.BikeLocation(
            bike_number=bike_number,
            current_station=station,
            last_seen=last_movement.end_time
        )

    def get_all_bikes_summary(self, skip: int, limit: int):
        summaries = self.bike_repo.get_all_summary(skip, limit)
        return [
            bike_schemas.BikeSummary(
                bike_number=bike_number,
                total_trips=total_trips,
                total_distance_km=round(total_distance_km, 2) if total_distance_km else 0.0,
                current_location=station
            )
            for bike_number, total_trips, total_distance_km, station in summaries
        ]
