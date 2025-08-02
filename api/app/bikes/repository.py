from datetime import datetime, timedelta
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased

from app.shared.repository import BaseRepository
from shared_models.models import BikeMovement, Station


class BikeRepository(BaseRepository):
    def get_movements(self, bike_number: str, skip: int = 0, limit: int = 25, days_back: int = 30, start_date: datetime = None, end_date: datetime = None):
        """
        Get bike movements with optional time-based filtering for better TimescaleDB performance.
        
        Args:
            bike_number: The bike to get movements for
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            days_back: Number of days back to look (default 30, ignored if start_date provided)
            start_date: Explicit start date filter (overrides days_back)
            end_date: Explicit end date filter (optional)
        """
        start_station = aliased(Station)
        end_station = aliased(Station)
        
        query = (
            self.db.query(BikeMovement, start_station, end_station)
            .join(start_station, BikeMovement.start_station_uid == start_station.uid)
            .join(end_station, BikeMovement.end_station_uid == end_station.uid)
            .filter(BikeMovement.bike_number == bike_number)
        )
        
        # Add time-based filtering to leverage TimescaleDB partitioning
        if start_date is not None:
            query = query.filter(BikeMovement.start_time >= start_date)
        elif days_back is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(BikeMovement.start_time >= cutoff_date)
            
        if end_date is not None:
            query = query.filter(BikeMovement.start_time <= end_date)
        
        return (
            query
            .order_by(desc(BikeMovement.start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_movement(self, bike_number: str, days_back: int = 30):
        """
        Get the latest movement for a bike with time-based filtering for better performance.
        
        Args:
            bike_number: The bike to get the latest movement for
            days_back: Number of days back to look (default 30)
        """
        query = (
            self.db.query(BikeMovement)
            .filter(BikeMovement.bike_number == bike_number)
        )
        
        # Add time-based filtering to reduce chunk scanning
        if days_back is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(BikeMovement.start_time >= cutoff_date)
        
        return (
            query
            .order_by(desc(BikeMovement.end_time))
            .first()
        )

    def get_all_summary(self, skip: int = 0, limit: int = 100):
        summary_sq = (
            self.db.query(
                BikeMovement.bike_number,
                func.count().label("total_trips"),
                func.sum(BikeMovement.distance_km).label("total_distance_km"),
            )
            .group_by(BikeMovement.bike_number)
            .subquery()
        )

        latest_movement_sq = (
            self.db.query(
                BikeMovement.bike_number, BikeMovement.end_station_uid
            )
            .distinct(BikeMovement.bike_number)
            .order_by(
                BikeMovement.bike_number, desc(BikeMovement.end_time)
            )
            .subquery()
        )

        return (
            self.db.query(
                summary_sq.c.bike_number,
                summary_sq.c.total_trips,
                summary_sq.c.total_distance_km,
                Station,
            )
            .join(
                latest_movement_sq,
                latest_movement_sq.c.bike_number == summary_sq.c.bike_number,
            )
            .join(
                Station,
                Station.uid == latest_movement_sq.c.end_station_uid,
            )
            .order_by(desc(summary_sq.c.total_distance_km))
            .offset(skip)
            .limit(limit)
            .all()
        )