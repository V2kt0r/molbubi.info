from datetime import datetime
from app.shared.exceptions import BikeNotFound
from app.bikes.repository import BikeRepository
from app.stations.repository import StationRepository
from app.bikes import schema as bike_schemas


class BikeService:
    def __init__(self, bike_repo: BikeRepository, station_repo: StationRepository):
        self.bike_repo = bike_repo
        self.station_repo = station_repo

    def get_bike_history(self, bike_number: str, skip: int, limit: int, days_back: int = 30, start_date: datetime = None, end_date: datetime = None):
        """
        Get bike movement history with optional time filtering for better performance.
        
        Args:
            bike_number: The bike to get movements for
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            days_back: Number of days back to look (default 30, ignored if start_date provided)
            start_date: Explicit start date filter (overrides days_back)
            end_date: Explicit end date filter (optional)
        """
        movements_data = self.bike_repo.get_movements(
            bike_number, skip, limit, days_back, start_date, end_date
        )
        return [
            bike_schemas.BikeMovement(
                bike_number=movement.bike_number,
                start_station=start_station,
                end_station=end_station,
                start_time=movement.start_time,
                end_time=movement.end_time,
                distance_km=movement.distance_km,
            )
            for movement, start_station, end_station in movements_data
        ]

    def get_current_location(self, bike_number: str):
        last_movement = self.bike_repo.get_latest_movement(bike_number)
        if not last_movement:
            raise BikeNotFound(bike_number)

        station = self.station_repo.get_by_uid(last_movement.end_station_uid)
        return bike_schemas.BikeLocation(
            bike_number=bike_number,
            current_station=station,
            last_seen=last_movement.end_time,
        )

    def get_all_bikes_summary(self, skip: int, limit: int):
        summaries = self.bike_repo.get_all_summary(skip, limit)
        return [
            bike_schemas.BikeSummary(
                bike_number=bike_number,
                total_trips=total_trips,
                total_distance_km=(
                    round(total_distance_km, 2) if total_distance_km else 0.0
                ),
                current_location=station,
            )
            for bike_number, total_trips, total_distance_km, station in summaries
        ]
