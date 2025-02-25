from fastapi import HTTPException, status


class BikeNotFoundException(HTTPException):
    def __init__(self, bike_number: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bike {bike_number} not found",
        )
