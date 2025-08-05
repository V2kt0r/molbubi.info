"""
Comprehensive tests for Pydantic schemas covering all edge cases.
"""
import json
import time
import pytest
from pydantic import ValidationError

from app.schemas.bike_data import Bike, Station, City, Country, ApiResponse, BikeState


class TestBike:
    """Test cases for Bike schema."""

    def test_bike_valid_creation(self):
        """Test creating a valid bike."""
        bike = Bike(number="BIKE123")
        assert bike.number == "BIKE123"

    def test_bike_with_empty_number(self):
        """Test bike with empty number."""
        bike = Bike(number="")
        assert bike.number == ""

    def test_bike_with_numeric_number(self):
        """Test bike with numeric number as string."""
        bike = Bike(number="12345")
        assert bike.number == "12345"

    def test_bike_with_special_characters(self):
        """Test bike with special characters in number."""
        bike = Bike(number="BIKE-123_ABC#456")
        assert bike.number == "BIKE-123_ABC#456"

    def test_bike_with_unicode_characters(self):
        """Test bike with unicode characters."""
        bike = Bike(number="自行车123")
        assert bike.number == "自行车123"

    def test_bike_with_very_long_number(self):
        """Test bike with very long number."""
        long_number = "BIKE" + "X" * 1000
        bike = Bike(number=long_number)
        assert bike.number == long_number

    def test_bike_missing_number(self):
        """Test bike creation without number."""
        with pytest.raises(ValidationError) as exc_info:
            Bike()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('number',)
        assert errors[0]['type'] == 'missing'

    def test_bike_invalid_number_type(self):
        """Test bike with invalid number type."""
        with pytest.raises(ValidationError) as exc_info:
            Bike(number=123)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('number',)
        assert 'str_type' in errors[0]['type'] or 'string_type' in errors[0]['type']


class TestStation:
    """Test cases for Station schema."""

    def test_station_valid_creation(self):
        """Test creating a valid station."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Test Station",
            spot=True,
            bike_list=[Bike(number="BIKE123")]
        )
        
        assert station.uid == 1001
        assert station.lat == 47.5
        assert station.lng == 19.0
        assert station.name == "Test Station"
        assert station.spot is True
        assert len(station.bike_list) == 1
        assert station.bike_list[0].number == "BIKE123"

    def test_station_with_empty_bike_list(self):
        """Test station with empty bike list."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Empty Station",
            spot=True,
            bike_list=[]
        )
        
        assert len(station.bike_list) == 0

    def test_station_without_bike_list(self):
        """Test station without bike_list field (should default to empty list)."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Default Station",
            spot=True
        )
        
        assert station.bike_list == []

    def test_station_with_multiple_bikes(self):
        """Test station with multiple bikes."""
        bikes = [Bike(number=f"BIKE{i}") for i in range(10)]
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Multi Bike Station",
            spot=True,
            bike_list=bikes
        )
        
        assert len(station.bike_list) == 10
        for i, bike in enumerate(station.bike_list):
            assert bike.number == f"BIKE{i}"

    def test_station_with_negative_coordinates(self):
        """Test station with negative coordinates."""
        station = Station(
            uid=1001,
            lat=-47.5,
            lng=-19.0,
            name="Southern Station",
            spot=True
        )
        
        assert station.lat == -47.5
        assert station.lng == -19.0

    def test_station_with_zero_coordinates(self):
        """Test station at coordinates (0, 0)."""
        station = Station(
            uid=1001,
            lat=0.0,
            lng=0.0,
            name="Origin Station",
            spot=True
        )
        
        assert station.lat == 0.0
        assert station.lng == 0.0

    def test_station_with_extreme_coordinates(self):
        """Test station with extreme coordinate values."""
        station = Station(
            uid=1001,
            lat=89.999,
            lng=179.999,
            name="Extreme Station",
            spot=True
        )
        
        assert station.lat == 89.999
        assert station.lng == 179.999

    def test_station_with_unicode_name(self):
        """Test station with unicode name."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Főváros állomás 🚲",
            spot=True
        )
        
        assert station.name == "Főváros állomás 🚲"

    def test_station_with_empty_name(self):
        """Test station with empty name."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="",
            spot=True
        )
        
        assert station.name == ""

    def test_station_spot_false(self):
        """Test station with spot=False."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Non-Spot Station",
            spot=False
        )
        
        assert station.spot is False

    def test_station_missing_required_fields(self):
        """Test station creation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Station()
        
        errors = exc_info.value.errors()
        required_fields = {'uid', 'lat', 'lng', 'name', 'spot'}
        error_fields = {error['loc'][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_station_invalid_uid_type(self):
        """Test station with invalid UID type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid="not_an_integer",
                lat=47.5,
                lng=19.0,
                name="Invalid UID",
                spot=True
            )
        
        errors = exc_info.value.errors()
        uid_errors = [error for error in errors if error['loc'][0] == 'uid']
        assert len(uid_errors) > 0

    def test_station_invalid_coordinate_types(self):
        """Test station with invalid coordinate types."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=1001,
                lat="not_a_float",
                lng="also_not_a_float",
                name="Invalid Coords",
                spot=True
            )
        
        errors = exc_info.value.errors()
        coord_errors = [error for error in errors if error['loc'][0] in ('lat', 'lng')]
        assert len(coord_errors) >= 2

    def test_station_invalid_spot_type(self):
        """Test station with invalid spot type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=1001,
                lat=47.5,
                lng=19.0,
                name="Invalid Spot",
                spot="not_a_boolean"
            )
        
        errors = exc_info.value.errors()
        spot_errors = [error for error in errors if error['loc'][0] == 'spot']
        assert len(spot_errors) > 0


class TestCity:
    """Test cases for City schema."""

    def test_city_valid_creation(self):
        """Test creating a valid city."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Test Station",
            spot=True
        )
        city = City(places=[station])
        
        assert len(city.places) == 1
        assert city.places[0].uid == 1001

    def test_city_empty_places(self):
        """Test city with empty places list."""
        city = City(places=[])
        assert city.places == []

    def test_city_without_places(self):
        """Test city without places field (should default to empty list)."""
        city = City()
        assert city.places == []

    def test_city_multiple_stations(self):
        """Test city with multiple stations."""
        stations = [
            Station(uid=i, lat=47.0 + i * 0.1, lng=19.0 + i * 0.1, 
                   name=f"Station {i}", spot=True)
            for i in range(5)
        ]
        city = City(places=stations)
        
        assert len(city.places) == 5
        for i, station in enumerate(city.places):
            assert station.uid == i
            assert station.name == f"Station {i}"


class TestCountry:
    """Test cases for Country schema."""

    def test_country_valid_creation(self):
        """Test creating a valid country."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Test Station",
            spot=True
        )
        city = City(places=[station])
        country = Country(cities=[city])
        
        assert len(country.cities) == 1
        assert len(country.cities[0].places) == 1

    def test_country_empty_cities(self):
        """Test country with empty cities list."""
        country = Country(cities=[])
        assert country.cities == []

    def test_country_without_cities(self):
        """Test country without cities field (should default to empty list)."""
        country = Country()
        assert country.cities == []

    def test_country_multiple_cities(self):
        """Test country with multiple cities."""
        cities = [City(places=[]) for _ in range(3)]
        country = Country(cities=cities)
        
        assert len(country.cities) == 3


class TestApiResponse:
    """Test cases for ApiResponse schema."""

    def test_api_response_valid_creation(self):
        """Test creating a valid API response."""
        station = Station(
            uid=1001,
            lat=47.5,
            lng=19.0,
            name="Test Station",
            spot=True,
            bike_list=[Bike(number="BIKE123")]
        )
        city = City(places=[station])
        country = Country(cities=[city])
        response = ApiResponse(countries=[country])
        
        assert len(response.countries) == 1
        assert len(response.countries[0].cities) == 1
        assert len(response.countries[0].cities[0].places) == 1
        assert len(response.countries[0].cities[0].places[0].bike_list) == 1

    def test_api_response_empty_countries(self):
        """Test API response with empty countries list."""
        response = ApiResponse(countries=[])
        assert response.countries == []

    def test_api_response_without_countries(self):
        """Test API response without countries field (should default to empty list)."""
        response = ApiResponse()
        assert response.countries == []

    def test_api_response_multiple_countries(self):
        """Test API response with multiple countries."""
        countries = [Country(cities=[]) for _ in range(3)]
        response = ApiResponse(countries=countries)
        
        assert len(response.countries) == 3

    def test_api_response_complex_structure(self):
        """Test API response with complex nested structure."""
        bikes = [Bike(number=f"BIKE{i}") for i in range(3)]
        stations = [
            Station(uid=j, lat=47.0 + j * 0.1, lng=19.0 + j * 0.1,
                   name=f"Station {j}", spot=True, bike_list=bikes)
            for j in range(2)
        ]
        cities = [City(places=stations) for _ in range(2)]
        countries = [Country(cities=cities) for _ in range(2)]
        response = ApiResponse(countries=countries)
        
        assert len(response.countries) == 2
        assert len(response.countries[0].cities) == 2
        assert len(response.countries[0].cities[0].places) == 2
        assert len(response.countries[0].cities[0].places[0].bike_list) == 3

    def test_api_response_from_json(self):
        """Test creating API response from JSON."""
        json_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 1001,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "JSON Station",
                                    "spot": True,
                                    "bike_list": [
                                        {"number": "BIKE123"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        response = ApiResponse(**json_data)
        assert response.countries[0].cities[0].places[0].name == "JSON Station"
        assert response.countries[0].cities[0].places[0].bike_list[0].number == "BIKE123"

    def test_api_response_invalid_structure(self):
        """Test API response with invalid structure."""
        with pytest.raises(ValidationError):
            ApiResponse(countries="not_a_list")


class TestBikeState:
    """Test cases for BikeState schema."""

    def test_bike_state_valid_creation(self):
        """Test creating a valid bike state."""
        state = BikeState(station_uid=1001, timestamp=1640995200.0, stay_start_time=1640995200.0)
        
        assert state.station_uid == 1001
        assert state.timestamp == 1640995200.0
        assert state.stay_start_time == 1640995200.0

    def test_bike_state_without_timestamp(self):
        """Test bike state without timestamp (should use current time)."""
        current_time = time.time()
        state = BikeState(station_uid=1001)
        
        # Check that timestamp is close to current time (within 1 second)
        assert abs(state.timestamp - current_time) < 1.0
        assert state.station_uid == 1001
        assert state.stay_start_time is None

    def test_bike_state_without_stay_start_time(self):
        """Test bike state without stay_start_time (should default to None)."""
        state = BikeState(station_uid=1001, timestamp=1640995200.0)
        
        assert state.station_uid == 1001
        assert state.timestamp == 1640995200.0
        assert state.stay_start_time is None

    def test_bike_state_with_negative_timestamp(self):
        """Test bike state with negative timestamp."""
        state = BikeState(station_uid=1001, timestamp=-1.0)
        
        assert state.timestamp == -1.0

    def test_bike_state_with_zero_timestamp(self):
        """Test bike state with zero timestamp."""
        state = BikeState(station_uid=1001, timestamp=0.0)
        
        assert state.timestamp == 0.0

    def test_bike_state_with_very_large_timestamp(self):
        """Test bike state with very large timestamp."""
        large_timestamp = 9999999999.0
        state = BikeState(station_uid=1001, timestamp=large_timestamp)
        
        assert state.timestamp == large_timestamp

    def test_bike_state_missing_station_uid(self):
        """Test bike state creation without station_uid."""
        with pytest.raises(ValidationError) as exc_info:
            BikeState()
        
        errors = exc_info.value.errors()
        uid_errors = [error for error in errors if error['loc'][0] == 'station_uid']
        assert len(uid_errors) > 0

    def test_bike_state_invalid_station_uid_type(self):
        """Test bike state with invalid station_uid type."""
        with pytest.raises(ValidationError) as exc_info:
            BikeState(station_uid="not_an_integer")
        
        errors = exc_info.value.errors()
        uid_errors = [error for error in errors if error['loc'][0] == 'station_uid']
        assert len(uid_errors) > 0

    def test_bike_state_invalid_timestamp_type(self):
        """Test bike state with invalid timestamp type."""
        with pytest.raises(ValidationError) as exc_info:
            BikeState(station_uid=1001, timestamp="not_a_float")
        
        errors = exc_info.value.errors()
        timestamp_errors = [error for error in errors if error['loc'][0] == 'timestamp']
        assert len(timestamp_errors) > 0

    def test_bike_state_json_serialization(self):
        """Test bike state JSON serialization."""
        state = BikeState(station_uid=1001, timestamp=1640995200.0, stay_start_time=1640995200.0)
        
        json_str = state.model_dump_json()
        parsed_data = json.loads(json_str)
        
        assert parsed_data['station_uid'] == 1001
        assert parsed_data['timestamp'] == 1640995200.0
        assert parsed_data['stay_start_time'] == 1640995200.0

    def test_bike_state_json_deserialization(self):
        """Test bike state JSON deserialization."""
        json_str = '{"station_uid": 1001, "timestamp": 1640995200.0, "stay_start_time": 1640995200.0}'
        
        state = BikeState.model_validate_json(json_str)
        
        assert state.station_uid == 1001
        assert state.timestamp == 1640995200.0
        assert state.stay_start_time == 1640995200.0

    def test_bike_state_model_dump(self):
        """Test bike state model dump."""
        state = BikeState(station_uid=1001, timestamp=1640995200.0, stay_start_time=1640995200.0)
        
        dumped = state.model_dump()
        
        assert dumped == {
            'station_uid': 1001,
            'timestamp': 1640995200.0,
            'stay_start_time': 1640995200.0
        }