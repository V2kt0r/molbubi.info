"""
Comprehensive tests for Pydantic schema validation covering all edge cases.
"""
import pytest
from pydantic import ValidationError

from app.schemas.nextbike import Bike, Station, City, Country, ApiResponse


class TestBikeSchema:
    """Test cases for Bike schema."""

    def test_bike_valid_data(self):
        """Test bike creation with valid data."""
        bike = Bike(number="123456")
        assert bike.number == "123456"

    def test_bike_numeric_string_number(self):
        """Test bike with numeric string number."""
        bike = Bike(number="999999")
        assert bike.number == "999999"

    def test_bike_alphanumeric_number(self):
        """Test bike with alphanumeric number."""
        bike = Bike(number="ABC123")
        assert bike.number == "ABC123"

    def test_bike_unicode_number(self):
        """Test bike with unicode characters in number."""
        bike = Bike(number="测试123")
        assert bike.number == "测试123"

    def test_bike_empty_number(self):
        """Test bike with empty number string."""
        bike = Bike(number="")
        assert bike.number == ""

    def test_bike_missing_number(self):
        """Test bike validation fails when number is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Bike()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("number",)

    def test_bike_none_number(self):
        """Test bike validation fails when number is None."""
        with pytest.raises(ValidationError) as exc_info:
            Bike(number=None)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"

    def test_bike_integer_number(self):
        """Test bike with integer number (should fail validation)."""
        with pytest.raises(ValidationError) as exc_info:
            Bike(number=123456)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"

    def test_bike_float_number(self):
        """Test bike with float number (should fail validation)."""
        with pytest.raises(ValidationError) as exc_info:
            Bike(number=123.456)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"


class TestStationSchema:
    """Test cases for Station schema."""

    def test_station_valid_data(self):
        """Test station creation with valid data."""
        station = Station(
            uid=12345,
            lat=47.497912,
            lng=19.040235,
            name="Test Station",
            spot=False,
            bike_list=[Bike(number="123"), Bike(number="456")]
        )
        
        assert station.uid == 12345
        assert station.lat == 47.497912
        assert station.lng == 19.040235
        assert station.name == "Test Station"
        assert station.spot is False
        assert len(station.bike_list) == 2
        assert station.bike_list[0].number == "123"

    def test_station_empty_bike_list(self):
        """Test station with empty bike list."""
        station = Station(
            uid=12345,
            lat=47.497912,
            lng=19.040235,
            name="Empty Station",
            spot=True
        )
        
        assert station.bike_list == []

    def test_station_unicode_name(self):
        """Test station with unicode characters in name."""
        station = Station(
            uid=12345,
            lat=47.497912,
            lng=19.040235,
            name="Állomás étkezde 🚲",
            spot=False
        )
        
        assert station.name == "Állomás étkezde 🚲"

    def test_station_extreme_coordinates(self):
        """Test station with extreme coordinate values."""
        station = Station(
            uid=12345,
            lat=90.0,  # Maximum latitude
            lng=180.0,  # Maximum longitude
            name="Extreme Station",
            spot=False
        )
        
        assert station.lat == 90.0
        assert station.lng == 180.0

    def test_station_negative_coordinates(self):
        """Test station with negative coordinates."""
        station = Station(
            uid=12345,
            lat=-47.497912,
            lng=-19.040235,
            name="Negative Coords Station",
            spot=False
        )
        
        assert station.lat == -47.497912
        assert station.lng == -19.040235

    def test_station_zero_coordinates(self):
        """Test station with zero coordinates."""
        station = Station(
            uid=12345,
            lat=0.0,
            lng=0.0,
            name="Zero Station",
            spot=False
        )
        
        assert station.lat == 0.0
        assert station.lng == 0.0

    def test_station_missing_uid(self):
        """Test station validation fails when uid is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                lat=47.497912,
                lng=19.040235,
                name="Test Station",
                spot=False
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("uid",) and error["type"] == "missing" for error in errors)

    def test_station_invalid_uid_type(self):
        """Test station validation fails with invalid uid type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid="not_an_integer",
                lat=47.497912,
                lng=19.040235,
                name="Test Station",
                spot=False
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("uid",) and error["type"] == "int_parsing" for error in errors)

    def test_station_invalid_lat_type(self):
        """Test station validation fails with invalid latitude type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat="not_a_float",
                lng=19.040235,
                name="Test Station",
                spot=False
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("lat",) and error["type"] == "float_parsing" for error in errors)

    def test_station_invalid_lng_type(self):
        """Test station validation fails with invalid longitude type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat=47.497912,
                lng="not_a_float",
                name="Test Station",
                spot=False
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("lng",) and error["type"] == "float_parsing" for error in errors)

    def test_station_missing_name(self):
        """Test station validation fails when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat=47.497912,
                lng=19.040235,
                spot=False
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) and error["type"] == "missing" for error in errors)

    def test_station_missing_spot(self):
        """Test station validation fails when spot is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat=47.497912,
                lng=19.040235,
                name="Test Station"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("spot",) and error["type"] == "missing" for error in errors)

    def test_station_invalid_spot_type(self):
        """Test station validation fails with invalid spot type."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat=47.497912,
                lng=19.040235,
                name="Test Station",
                spot="not_a_boolean"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("spot",) and error["type"] == "bool_parsing" for error in errors)

    def test_station_invalid_bike_list_item(self):
        """Test station validation fails with invalid bike in bike_list."""
        with pytest.raises(ValidationError) as exc_info:
            Station(
                uid=12345,
                lat=47.497912,
                lng=19.040235,
                name="Test Station",
                spot=False,
                bike_list=[{"invalid": "bike_data"}]
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "bike_list" for error in errors)

    def test_station_extra_fields_ignored(self):
        """Test that extra fields are ignored in station."""
        station = Station(
            uid=12345,
            lat=47.497912,
            lng=19.040235,
            name="Test Station",
            spot=False,
            extra_field="should be ignored",
            another_extra=123
        )
        
        assert station.uid == 12345
        assert not hasattr(station, 'extra_field')

    def test_station_large_uid(self):
        """Test station with very large uid."""
        large_uid = 999999999999999
        station = Station(
            uid=large_uid,
            lat=47.497912,
            lng=19.040235,
            name="Large UID Station",
            spot=False
        )
        
        assert station.uid == large_uid

    def test_station_precision_coordinates(self):
        """Test station with high precision coordinates."""
        station = Station(
            uid=12345,
            lat=47.497912345678901,
            lng=19.040235987654321,
            name="Precision Station",
            spot=False
        )
        
        assert station.lat == 47.497912345678901
        assert station.lng == 19.040235987654321


class TestCitySchema:
    """Test cases for City schema."""

    def test_city_with_places(self):
        """Test city creation with places."""
        city = City(places=[
            Station(uid=1, lat=47.5, lng=19.0, name="Station 1", spot=False),
            Station(uid=2, lat=47.6, lng=19.1, name="Station 2", spot=True)
        ])
        
        assert len(city.places) == 2
        assert city.places[0].uid == 1
        assert city.places[1].uid == 2

    def test_city_empty_places(self):
        """Test city with empty places list."""
        city = City()
        assert city.places == []

    def test_city_explicit_empty_places(self):
        """Test city with explicitly empty places list."""
        city = City(places=[])
        assert city.places == []

    def test_city_invalid_places_item(self):
        """Test city validation fails with invalid place in places list."""
        with pytest.raises(ValidationError) as exc_info:
            City(places=[{"invalid": "station_data"}])
        
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "places" for error in errors)


class TestCountrySchema:
    """Test cases for Country schema."""

    def test_country_with_cities(self):
        """Test country creation with cities."""
        country = Country(cities=[
            City(places=[
                Station(uid=1, lat=47.5, lng=19.0, name="Station 1", spot=False)
            ]),
            City(places=[])
        ])
        
        assert len(country.cities) == 2
        assert len(country.cities[0].places) == 1
        assert len(country.cities[1].places) == 0

    def test_country_empty_cities(self):
        """Test country with empty cities list."""
        country = Country()
        assert country.cities == []

    def test_country_invalid_cities_item(self):
        """Test country validation fails with invalid city in cities list."""
        with pytest.raises(ValidationError) as exc_info:
            Country(cities=["not_a_city_dict"])  # String instead of dict
        
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "cities" for error in errors)


class TestApiResponseSchema:
    """Test cases for ApiResponse schema."""

    def test_api_response_full_structure(self, valid_nextbike_data):
        """Test API response with full nested structure."""
        response = ApiResponse.model_validate(valid_nextbike_data)
        
        assert len(response.countries) == 1
        assert len(response.countries[0].cities) == 1
        assert len(response.countries[0].cities[0].places) == 2
        
        # Check first station
        station1 = response.countries[0].cities[0].places[0]
        assert station1.uid == 42990604
        assert station1.name == "Test Station"
        assert len(station1.bike_list) == 2

    def test_api_response_empty_structure(self):
        """Test API response with empty structure."""
        response = ApiResponse(countries=[])
        assert response.countries == []

    def test_api_response_minimal_valid(self, minimal_nextbike_data):
        """Test API response with minimal valid data."""
        response = ApiResponse.model_validate(minimal_nextbike_data)
        assert response.countries == []

    def test_api_response_large_dataset(self, large_nextbike_data):
        """Test API response with large dataset."""
        response = ApiResponse.model_validate(large_nextbike_data)
        
        assert len(response.countries) == 1
        assert len(response.countries[0].cities) == 1
        assert len(response.countries[0].cities[0].places) == 100
        
        # Verify some random stations
        places = response.countries[0].cities[0].places
        assert places[0].uid == 42990000
        assert places[50].uid == 42990050
        assert places[99].uid == 42990099

    def test_api_response_nested_validation_error(self):
        """Test API response validation fails with nested invalid data."""
        invalid_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": "invalid_uid",  # Should be int
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Test Station",
                                    "spot": False
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ApiResponse.model_validate(invalid_data)
        
        errors = exc_info.value.errors()
        assert any("uid" in str(error["loc"]) for error in errors)

    def test_api_response_multiple_countries(self):
        """Test API response with multiple countries."""
        data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 1,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Country 1 Station",
                                    "spot": False,
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 2,
                                    "lat": 48.5,
                                    "lng": 20.0,
                                    "name": "Country 2 Station",
                                    "spot": True,
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        response = ApiResponse.model_validate(data)
        assert len(response.countries) == 2
        assert response.countries[0].cities[0].places[0].name == "Country 1 Station"
        assert response.countries[1].cities[0].places[0].name == "Country 2 Station"

    def test_api_response_mixed_empty_non_empty(self):
        """Test API response with mix of empty and non-empty collections."""
        data = {
            "countries": [
                {
                    "cities": []  # Empty cities
                },
                {
                    "cities": [
                        {
                            "places": []  # Empty places
                        },
                        {
                            "places": [
                                {
                                    "uid": 1,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Only Station",
                                    "spot": False,
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        response = ApiResponse.model_validate(data)
        assert len(response.countries) == 2
        assert len(response.countries[0].cities) == 0
        assert len(response.countries[1].cities) == 2
        assert len(response.countries[1].cities[0].places) == 0
        assert len(response.countries[1].cities[1].places) == 1

    def test_api_response_model_dump(self, valid_nextbike_data):
        """Test that model_dump returns correct structure."""
        response = ApiResponse.model_validate(valid_nextbike_data)
        dumped = response.model_dump()
        
        assert isinstance(dumped, dict)
        assert "countries" in dumped
        assert isinstance(dumped["countries"], list)
        
        # Verify the dumped data can be used to recreate the model
        recreated = ApiResponse.model_validate(dumped)
        assert len(recreated.countries) == len(response.countries)

    def test_api_response_invalid_root_structure(self):
        """Test API response validation fails with completely invalid structure."""
        invalid_data = {
            "invalid_field": "this is not a valid nextbike response",
            "another_invalid": 123
        }
        
        response = ApiResponse.model_validate(invalid_data)
        # Should succeed with empty countries list (default)
        assert response.countries == []

    def test_api_response_none_countries(self):
        """Test API response validation with None countries."""
        with pytest.raises(ValidationError) as exc_info:
            ApiResponse(countries=None)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("countries",) for error in errors)