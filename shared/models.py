from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Double, ForeignKey, Index, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class StationModel(Base):
    __tablename__ = "stations"

    uid = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Double)
    lng = Column(Double)

    bikes = relationship("BikeModel", back_populates="station")

    __table_args__ = (Index("idx_station_location", lat, lng),)


class BikeModel(Base):
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True)
    number = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now(UTC), index=True)
    station_uid = Column(Integer, ForeignKey("stations.uid"), index=True)

    station = relationship("StationModel", back_populates="bikes")
