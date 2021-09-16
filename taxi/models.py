from datetime import datetime

from sqlalchemy import Integer, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData, Column

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class DriverRoute(Base):
    __tablename__ = 'driver_route'

    id = Column(Integer, primary_key=True, nullable=False)
    driver_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.now, nullable=False)


class RouteDescription(Base):
    __tablename__ = 'route_description'

    id = Column(Integer, primary_key=True, nullable=False)
    driver_route_id = Column(Integer, nullable=False)
    is_driver_over_speed = Column(Boolean, nullable=False)
    is_correct_driver_altitude = Column(Boolean, nullable=False)
    date_created = Column(DateTime, default=datetime.now, nullable=False)
