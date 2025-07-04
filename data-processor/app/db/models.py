from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
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

    # Define columns without a single primary key here
    bike_number = Column(String, index=True, nullable=False)
    start_time = Column(
        DateTime(timezone=True), nullable=False
    )  # This is the partitioning column

    end_time = Column(DateTime(timezone=True), nullable=False)
    start_station_uid = Column(Integer, ForeignKey("stations.uid"))
    end_station_uid = Column(Integer, ForeignKey("stations.uid"))
    distance_km = Column(Float)

    # Define a composite primary key that includes the partitioning column
    __table_args__ = (
        PrimaryKeyConstraint("bike_number", "start_time"),
        {},
    )
