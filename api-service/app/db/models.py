from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
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

    bike_number = Column(String, index=True, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)

    end_time = Column(DateTime(timezone=True), nullable=False)
    start_station_uid = Column(Integer, ForeignKey("stations.uid"))
    end_station_uid = Column(Integer, ForeignKey("stations.uid"))
    distance_km = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("bike_number", "start_time"),
        {},
    )
