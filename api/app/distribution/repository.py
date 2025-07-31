from datetime import date
from sqlalchemy import func, extract

from app.shared.repository import BaseRepository
from app.shared import models


class DistributionRepository(BaseRepository):
    def get_hourly_arrival_distribution(
        self, 
        start_date: date | None = None, 
        end_date: date | None = None, 
        station_uids: list[int] | None = None
    ) -> list[dict]:
        """
        Get hourly distribution of bike arrivals.
        
        Args:
            start_date: Filter arrivals from this date (inclusive)
            end_date: Filter arrivals until this date (inclusive)  
            station_uids: Filter arrivals to specific stations
            
        Returns:
            List of dicts with 'time' (hour 0-23) and 'arrival_count'
        """
        query = self.db.query(
            extract('hour', models.BikeMovement.end_time).label('hour'),
            func.count(models.BikeMovement.bike_number).label('arrival_count')
        ).filter(
            models.BikeMovement.end_time.isnot(None),
            models.BikeMovement.end_station_uid.isnot(None)
        )
        
        # Apply date range filter
        if start_date:
            query = query.filter(func.date(models.BikeMovement.end_time) >= start_date)
        if end_date:
            query = query.filter(func.date(models.BikeMovement.end_time) <= end_date)
            
        # Apply station filter
        if station_uids:
            query = query.filter(models.BikeMovement.end_station_uid.in_(station_uids))
            
        results = query.group_by(extract('hour', models.BikeMovement.end_time)).all()
        
        # Create a complete 24-hour distribution (fill missing hours with 0)
        hour_counts = {int(hour): count for hour, count in results}
        distribution = []
        for hour in range(24):
            distribution.append({
                'time': hour,
                'arrival_count': hour_counts.get(hour, 0)
            })
            
        return distribution

    def get_hourly_departure_distribution(
        self, 
        start_date: date | None = None, 
        end_date: date | None = None, 
        station_uids: list[int] | None = None
    ) -> list[dict]:
        """
        Get hourly distribution of bike departures.
        
        Args:
            start_date: Filter departures from this date (inclusive)
            end_date: Filter departures until this date (inclusive)  
            station_uids: Filter departures to specific stations
            
        Returns:
            List of dicts with 'time' (hour 0-23) and 'departure_count'
        """
        query = self.db.query(
            extract('hour', models.BikeMovement.start_time).label('hour'),
            func.count(models.BikeMovement.bike_number).label('departure_count')
        ).filter(
            models.BikeMovement.start_time.isnot(None),
            models.BikeMovement.start_station_uid.isnot(None)
        )
        
        # Apply date range filter
        if start_date:
            query = query.filter(func.date(models.BikeMovement.start_time) >= start_date)
        if end_date:
            query = query.filter(func.date(models.BikeMovement.start_time) <= end_date)
            
        # Apply station filter
        if station_uids:
            query = query.filter(models.BikeMovement.start_station_uid.in_(station_uids))
            
        results = query.group_by(extract('hour', models.BikeMovement.start_time)).all()
        
        # Create a complete 24-hour distribution (fill missing hours with 0)
        hour_counts = {int(hour): count for hour, count in results}
        distribution = []
        for hour in range(24):
            distribution.append({
                'time': hour,
                'departure_count': hour_counts.get(hour, 0)
            })
            
        return distribution