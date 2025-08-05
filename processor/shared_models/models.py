from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"
    uid = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    lat = Column(Float)
    lng = Column(Float)


class BikeMovement(Base):
    __tablename__ = "bike_movements"

    bike_number = Column(String, nullable=False)  # Removed individual index, using composite
    start_time = Column(DateTime(timezone=True), nullable=False)

    end_time = Column(DateTime(timezone=True), nullable=False)
    start_station_uid = Column(Integer, ForeignKey("stations.uid"))
    end_station_uid = Column(Integer, ForeignKey("stations.uid"))
    distance_km = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("bike_number", "start_time"),
        # Optimized composite indexes for query performance
        Index(
            "idx_bike_movements_bike_time_covering",
            "bike_number", 
            start_time.desc(),
            postgresql_include=["end_time", "start_station_uid", "end_station_uid", "distance_km"]
        ),
        Index(
            "idx_bike_movements_bike_endtime",
            "bike_number",
            end_time.desc()
        ),
        Index(
            "idx_bike_movements_start_station_stats",
            "start_station_uid",
            postgresql_include=["bike_number"]
        ),
        Index(
            "idx_bike_movements_end_station_stats", 
            "end_station_uid",
            postgresql_include=["bike_number"]
        ),
        {},
    )


class BikeStay(Base):
    __tablename__ = "bike_stays"
    
    bike_number = Column(String, primary_key=True, nullable=False)
    station_uid = Column(Integer, ForeignKey("stations.uid"), primary_key=True, nullable=False)
    start_time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    
    end_time = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('bike_number', 'station_uid', 'start_time'),
        {},
    )