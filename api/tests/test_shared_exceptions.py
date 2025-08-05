import pytest
from app.shared.exceptions import ApiException, ResourceNotFound, BikeNotFound, StationNotFound


class TestApiException:
    def test_init(self):
        detail = "Test error message"
        exception = ApiException(detail)
        
        assert exception.detail == detail

    def test_inheritance(self):
        exception = ApiException("test")
        assert isinstance(exception, Exception)

    def test_str_representation(self):
        detail = "Test error"
        exception = ApiException(detail)
        
        # Should be able to convert to string
        str(exception)


class TestResourceNotFound:
    def test_init(self):
        detail = "Resource not found"
        exception = ResourceNotFound(detail)
        
        assert exception.detail == detail

    def test_inheritance(self):
        exception = ResourceNotFound("test")
        assert isinstance(exception, ApiException)
        assert isinstance(exception, Exception)

    def test_can_be_raised(self):
        with pytest.raises(ResourceNotFound) as exc_info:
            raise ResourceNotFound("Test resource not found")
        
        assert exc_info.value.detail == "Test resource not found"


class TestBikeNotFound:
    def test_init(self):
        bike_number = "BIKE123"
        exception = BikeNotFound(bike_number)
        
        expected_detail = f"Bike with number '{bike_number}' not found."
        assert exception.detail == expected_detail

    def test_inheritance(self):
        exception = BikeNotFound("BIKE123")
        assert isinstance(exception, ResourceNotFound)
        assert isinstance(exception, ApiException)
        assert isinstance(exception, Exception)

    def test_can_be_raised(self):
        bike_number = "BIKE456"
        with pytest.raises(BikeNotFound) as exc_info:
            raise BikeNotFound(bike_number)
        
        expected_detail = f"Bike with number '{bike_number}' not found."
        assert exc_info.value.detail == expected_detail

    def test_different_bike_numbers(self):
        # Test with different bike number formats
        test_cases = ["BIKE123", "bike-456", "B789", "123", ""]
        
        for bike_number in test_cases:
            exception = BikeNotFound(bike_number)
            expected_detail = f"Bike with number '{bike_number}' not found."
            assert exception.detail == expected_detail

    def test_special_characters_in_bike_number(self):
        bike_number = "BIKE/123#!@"
        exception = BikeNotFound(bike_number)
        
        expected_detail = f"Bike with number '{bike_number}' not found."
        assert exception.detail == expected_detail


class TestStationNotFound:
    def test_init(self):
        station_uid = 123
        exception = StationNotFound(station_uid)
        
        expected_detail = f"Station with UID '{station_uid}' not found."
        assert exception.detail == expected_detail

    def test_inheritance(self):
        exception = StationNotFound(123)
        assert isinstance(exception, ResourceNotFound)
        assert isinstance(exception, ApiException)
        assert isinstance(exception, Exception)

    def test_can_be_raised(self):
        station_uid = 456
        with pytest.raises(StationNotFound) as exc_info:
            raise StationNotFound(station_uid)
        
        expected_detail = f"Station with UID '{station_uid}' not found."
        assert exc_info.value.detail == expected_detail

    def test_different_station_uids(self):
        # Test with different station UID values
        test_cases = [0, 1, 123, 999999, -1]
        
        for station_uid in test_cases:
            exception = StationNotFound(station_uid)
            expected_detail = f"Station with UID '{station_uid}' not found."
            assert exception.detail == expected_detail

    def test_negative_station_uid(self):
        station_uid = -1
        exception = StationNotFound(station_uid)
        
        expected_detail = f"Station with UID '{station_uid}' not found."
        assert exception.detail == expected_detail

    def test_zero_station_uid(self):
        station_uid = 0
        exception = StationNotFound(station_uid)
        
        expected_detail = f"Station with UID '{station_uid}' not found."
        assert exception.detail == expected_detail

    def test_large_station_uid(self):
        station_uid = 999999999
        exception = StationNotFound(station_uid)
        
        expected_detail = f"Station with UID '{station_uid}' not found."
        assert exception.detail == expected_detail


class TestExceptionChaining:
    def test_exception_chaining(self):
        # Test that exceptions can be chained properly
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise BikeNotFound("BIKE123") from e
        except BikeNotFound as bike_exc:
            assert bike_exc.__cause__ is not None
            assert isinstance(bike_exc.__cause__, ValueError)
            assert str(bike_exc.__cause__) == "Original error"

    def test_multiple_exception_types(self):
        # Test that different exception types can be handled together
        exceptions = [
            BikeNotFound("BIKE123"),
            StationNotFound(456),
            ResourceNotFound("Generic resource"),
            ApiException("API error")
        ]
        
        for exc in exceptions:
            with pytest.raises(type(exc)):
                raise exc