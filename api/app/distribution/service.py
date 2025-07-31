from datetime import date

from app.distribution.repository import DistributionRepository
from app.distribution.schema import HourlyDistribution


class DistributionService:
    def __init__(self, distribution_repo: DistributionRepository):
        self.distribution_repo = distribution_repo

    def get_hourly_arrival_distribution(
        self, 
        start_date: date | None = None, 
        end_date: date | None = None, 
        station_uids: list[int] | None = None
    ) -> list[HourlyDistribution]:
        """
        Get hourly distribution of bike arrivals with optional filtering.
        
        Args:
            start_date: Filter arrivals from this date (inclusive)
            end_date: Filter arrivals until this date (inclusive)
            station_uids: Filter arrivals to specific stations
            
        Returns:
            List of HourlyDistribution objects for each hour (0-23)
        """
        raw_data = self.distribution_repo.get_hourly_arrival_distribution(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )
        
        return [
            HourlyDistribution(
                time=item['time'],
                arrival_count=item['arrival_count']
            )
            for item in raw_data
        ]