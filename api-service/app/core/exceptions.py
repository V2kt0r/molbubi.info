class ApiException(Exception):
    """Base exception for all API-related errors."""

    def __init__(self, detail: str):
        self.detail = detail


class ResourceNotFound(ApiException):
    """Raised when a requested resource is not found."""

    pass


class BikeNotFound(ResourceNotFound):
    """Raised when a specific bike is not found."""

    def __init__(self, bike_number: str):
        super().__init__(detail=f"Bike with number '{bike_number}' not found.")


class StationNotFound(ResourceNotFound):
    """Raised when a specific station is not found."""

    def __init__(self, station_uid: int):
        super().__init__(detail=f"Station with UID '{station_uid}' not found.")
