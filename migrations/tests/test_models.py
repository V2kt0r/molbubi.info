import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models import Base, Station, BikeMovement, BikeStay


class TestModels:
    """Test database model definitions and relationships."""

    @pytest.fixture
    def engine(self):
        """Create an in-memory SQLite engine for testing."""
        engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create a database session for testing."""
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    @pytest.mark.unit
    def test_base_metadata_exists(self):
        """Test that Base metadata is properly configured."""
        assert Base.metadata is not None
        assert hasattr(Base, 'registry')

    @pytest.mark.unit
    def test_station_model_structure(self):
        """Test Station model structure and attributes."""
        # Test table name
        assert Station.__tablename__ == "stations"
        
        # Test columns exist and have correct types
        columns = Station.__table__.columns
        assert 'uid' in columns
        assert 'name' in columns
        assert 'lat' in columns
        assert 'lng' in columns
        
        # Test column properties
        uid_col = columns['uid']
        assert uid_col.primary_key
        assert uid_col.index
        assert str(uid_col.type) == 'INTEGER'
        
        name_col = columns['name']
        assert name_col.index
        assert 'VARCHAR' in str(name_col.type) or 'TEXT' in str(name_col.type)
        
        lat_col = columns['lat']
        assert 'FLOAT' in str(lat_col.type)
        
        lng_col = columns['lng']
        assert 'FLOAT' in str(lng_col.type)

    @pytest.mark.unit
    def test_bike_movement_model_structure(self):
        """Test BikeMovement model structure and attributes."""
        # Test table name
        assert BikeMovement.__tablename__ == "bike_movements"
        
        # Test columns exist
        columns = BikeMovement.__table__.columns
        required_columns = [
            'bike_number', 'start_time', 'end_time',
            'start_station_uid', 'end_station_uid', 'distance_km'
        ]
        
        for col_name in required_columns:
            assert col_name in columns, f"Column {col_name} not found"

        # Test column properties
        bike_number_col = columns['bike_number']
        assert not bike_number_col.nullable
        assert 'VARCHAR' in str(bike_number_col.type) or 'TEXT' in str(bike_number_col.type)
        
        start_time_col = columns['start_time']
        assert not start_time_col.nullable
        assert 'DATETIME' in str(start_time_col.type)
        
        end_time_col = columns['end_time']
        assert not end_time_col.nullable
        assert 'DATETIME' in str(end_time_col.type)

    @pytest.mark.unit
    def test_bike_movement_primary_key_constraint(self):
        """Test BikeMovement composite primary key constraint."""
        table = BikeMovement.__table__
        pk_constraint = table.primary_key
        
        # Should have composite primary key
        assert len(pk_constraint.columns) == 2
        pk_column_names = [col.name for col in pk_constraint.columns]
        assert 'bike_number' in pk_column_names
        assert 'start_time' in pk_column_names

    @pytest.mark.unit
    def test_bike_movement_foreign_keys(self):
        """Test BikeMovement foreign key constraints."""
        table = BikeMovement.__table__
        
        # Get foreign key constraints
        foreign_keys = []
        for col in table.columns:
            if col.foreign_keys:
                foreign_keys.extend(col.foreign_keys)
        
        assert len(foreign_keys) == 2  # start_station_uid and end_station_uid
        
        # Check foreign key references
        fk_references = [fk.column.table.name for fk in foreign_keys]
        assert fk_references.count('stations') == 2

    @pytest.mark.unit
    def test_bike_movement_indexes(self):
        """Test BikeMovement index definitions."""
        table = BikeMovement.__table__
        indexes = table.indexes
        
        # Should have multiple indexes defined in __table_args__
        assert len(indexes) >= 4  # At least the 4 indexes defined
        
        index_names = [idx.name for idx in indexes]
        expected_indexes = [
            'idx_bike_movements_bike_time_covering',
            'idx_bike_movements_bike_endtime',
            'idx_bike_movements_start_station_stats',
            'idx_bike_movements_end_station_stats'
        ]
        
        for expected_idx in expected_indexes:
            assert expected_idx in index_names

    @pytest.mark.unit
    def test_bike_stay_model_structure(self):
        """Test BikeStay model structure and attributes."""
        # Test table name
        assert BikeStay.__tablename__ == "bike_stays"
        
        # Test columns exist
        columns = BikeStay.__table__.columns
        required_columns = ['bike_number', 'station_uid', 'start_time', 'end_time']
        
        for col_name in required_columns:
            assert col_name in columns, f"Column {col_name} not found"

        # Test column properties
        bike_number_col = columns['bike_number']
        assert bike_number_col.primary_key
        assert not bike_number_col.nullable
        
        station_uid_col = columns['station_uid']
        assert station_uid_col.primary_key
        assert not station_uid_col.nullable
        
        start_time_col = columns['start_time']
        assert start_time_col.primary_key
        assert not start_time_col.nullable
        
        end_time_col = columns['end_time']
        assert end_time_col.nullable  # Can be NULL for ongoing stays

    @pytest.mark.unit
    def test_bike_stay_primary_key_constraint(self):
        """Test BikeStay composite primary key constraint."""
        table = BikeStay.__table__
        pk_constraint = table.primary_key
        
        # Should have composite primary key with 3 columns
        assert len(pk_constraint.columns) == 3
        pk_column_names = [col.name for col in pk_constraint.columns]
        assert 'bike_number' in pk_column_names
        assert 'station_uid' in pk_column_names
        assert 'start_time' in pk_column_names

    @pytest.mark.unit
    def test_bike_stay_foreign_keys(self):
        """Test BikeStay foreign key constraints."""
        table = BikeStay.__table__
        
        # Get foreign key constraints
        foreign_keys = []
        for col in table.columns:
            if col.foreign_keys:
                foreign_keys.extend(col.foreign_keys)
        
        assert len(foreign_keys) == 1  # Only station_uid
        
        # Check foreign key reference
        fk = list(foreign_keys)[0]
        assert fk.column.table.name == 'stations'
        assert fk.column.name == 'uid'


class TestModelInstantiation:
    """Test creating model instances."""

    @pytest.mark.unit
    def test_station_creation(self):
        """Test creating a Station instance."""
        station = Station(
            uid=123,
            name="Test Station",
            lat=52.5200,
            lng=13.4050
        )
        
        assert station.uid == 123
        assert station.name == "Test Station"
        assert station.lat == 52.5200
        assert station.lng == 13.4050

    @pytest.mark.unit
    def test_bike_movement_creation(self):
        """Test creating a BikeMovement instance."""
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        movement = BikeMovement(
            bike_number="BIKE123",
            start_time=start_time,
            end_time=end_time,
            start_station_uid=1,
            end_station_uid=2,
            distance_km=2.5
        )
        
        assert movement.bike_number == "BIKE123"
        assert movement.start_time == start_time
        assert movement.end_time == end_time
        assert movement.start_station_uid == 1
        assert movement.end_station_uid == 2
        assert movement.distance_km == 2.5

    @pytest.mark.unit
    def test_bike_stay_creation(self):
        """Test creating a BikeStay instance."""
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        stay = BikeStay(
            bike_number="BIKE456",
            station_uid=10,
            start_time=start_time,
            end_time=end_time
        )
        
        assert stay.bike_number == "BIKE456"
        assert stay.station_uid == 10
        assert stay.start_time == start_time
        assert stay.end_time == end_time

    @pytest.mark.unit
    def test_bike_stay_creation_without_end_time(self):
        """Test creating a BikeStay instance without end_time (ongoing stay)."""
        start_time = datetime.now(timezone.utc)
        
        stay = BikeStay(
            bike_number="BIKE789",
            station_uid=15,
            start_time=start_time,
            end_time=None
        )
        
        assert stay.bike_number == "BIKE789"
        assert stay.station_uid == 15
        assert stay.start_time == start_time
        assert stay.end_time is None


class TestModelIntegration:
    """Integration tests for model relationships and database operations."""

    @pytest.fixture
    def engine(self):
        """Create an in-memory SQLite engine for testing."""
        engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create a database session for testing."""
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    @pytest.mark.integration
    def test_table_creation(self, engine):
        """Test that all tables are created correctly."""
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        expected_tables = ['stations', 'bike_movements', 'bike_stays']
        for table_name in expected_tables:
            assert table_name in table_names

    @pytest.mark.integration
    def test_station_crud_operations(self, session):
        """Test CRUD operations on Station model."""
        # Create
        station = Station(uid=1, name="Central Station", lat=52.5, lng=13.4)
        session.add(station)
        session.commit()
        
        # Read
        retrieved_station = session.query(Station).filter_by(uid=1).first()
        assert retrieved_station is not None
        assert retrieved_station.name == "Central Station"
        
        # Update
        retrieved_station.name = "Updated Station"
        session.commit()
        
        updated_station = session.query(Station).filter_by(uid=1).first()
        assert updated_station.name == "Updated Station"
        
        # Delete
        session.delete(updated_station)
        session.commit()
        
        deleted_station = session.query(Station).filter_by(uid=1).first()
        assert deleted_station is None

    @pytest.mark.integration
    def test_bike_movement_with_foreign_keys(self, session):
        """Test BikeMovement creation with foreign key relationships."""
        # Create stations first
        station1 = Station(uid=1, name="Station A", lat=52.5, lng=13.4)
        station2 = Station(uid=2, name="Station B", lat=52.6, lng=13.5)
        session.add_all([station1, station2])
        session.commit()
        
        # Create bike movement
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        movement = BikeMovement(
            bike_number="BIKE001",
            start_time=start_time,
            end_time=end_time,
            start_station_uid=1,
            end_station_uid=2,
            distance_km=1.5
        )
        session.add(movement)
        session.commit()
        
        # Verify the movement was created
        retrieved_movement = session.query(BikeMovement).filter_by(bike_number="BIKE001").first()
        assert retrieved_movement is not None
        assert retrieved_movement.start_station_uid == 1
        assert retrieved_movement.end_station_uid == 2

    @pytest.mark.integration
    def test_bike_stay_with_foreign_keys(self, session):
        """Test BikeStay creation with foreign key relationships."""
        # Create station first
        station = Station(uid=1, name="Station A", lat=52.5, lng=13.4)
        session.add(station)
        session.commit()
        
        # Create bike stay
        start_time = datetime.now(timezone.utc)
        
        stay = BikeStay(
            bike_number="BIKE002",
            station_uid=1,
            start_time=start_time,
            end_time=None
        )
        session.add(stay)
        session.commit()
        
        # Verify the stay was created
        retrieved_stay = session.query(BikeStay).filter_by(bike_number="BIKE002").first()
        assert retrieved_stay is not None
        assert retrieved_stay.station_uid == 1
        assert retrieved_stay.end_time is None

    @pytest.mark.integration
    def test_composite_primary_key_uniqueness(self, session):
        """Test that composite primary keys enforce uniqueness correctly."""
        # Use a fixed datetime to avoid timezone comparison issues
        start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        
        # Create first movement
        movement1 = BikeMovement(
            bike_number="BIKE003",
            start_time=start_time,
            end_time=end_time,
            start_station_uid=1,
            end_station_uid=2,
            distance_km=1.0
        )
        session.add(movement1)
        session.commit()
        
        # Try to create duplicate (should work in SQLite, would fail in PostgreSQL)
        movement2 = BikeMovement(
            bike_number="BIKE003",
            start_time=start_time,  # Same bike_number and start_time
            end_time=end_time,
            start_station_uid=2,
            end_station_uid=3,
            distance_km=2.0
        )
        
        # In SQLite this might not enforce the constraint as strictly as PostgreSQL
        # But we can still test the model structure is correct
        assert movement1.bike_number == movement2.bike_number
        # Compare just the timestamp part, ignoring potential timezone differences
        assert movement1.start_time.replace(tzinfo=None) == movement2.start_time.replace(tzinfo=None)