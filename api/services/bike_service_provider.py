from .distance_service import DistanceCalculatorService
from .distribution_service import DistributionAnalysisService
from .history_service import HistoryQueryService


class BikeServiceProvider:
    @staticmethod
    def get_distance_service(repository):
        return DistanceCalculatorService(repository)

    @staticmethod
    def get_history_service(repository):
        return HistoryQueryService(repository)

    @staticmethod
    def get_distribution_service(repository):
        return DistributionAnalysisService(repository)
