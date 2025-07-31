from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi_restful.cbv import cbv

from app.distribution.schema import HourlyDistribution
from app.distribution.service import DistributionService
from app.shared.dependencies import get_distribution_service

router = APIRouter()


@cbv(router)
class DistributionCBV:
    service: DistributionService = Depends(get_distribution_service)

    @router.get("/hour", response_model=list[HourlyDistribution])
    def get_hourly_distribution(
        self,
        start_date: date | None = Query(None, description="Filter from this date (YYYY-MM-DD)"),
        end_date: date | None = Query(None, description="Filter until this date (YYYY-MM-DD)"),
        station_uids: list[int] | None = Query(None, description="Filter to specific station UIDs")
    ):
        """
        Get hourly distribution of bike arrivals.
        
        Returns 24 data points (one for each hour 0-23) showing arrival counts.
        Supports filtering by date range and specific stations.
        
        Example: /distribution/hour?start_date=2024-01-01&end_date=2024-01-31&station_uids=123&station_uids=456
        """
        return self.service.get_hourly_arrival_distribution(
            start_date=start_date,
            end_date=end_date,
            station_uids=station_uids
        )