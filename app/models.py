from sqlalchemy import Column, Float, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC

Base = declarative_base()


class SensorValue(Base):
    __tablename__ = "sensor_values"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    device_uuid = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    sensor_type = Column(String)
    value = Column(Float)
    unit = Column(String)


class PumpEvent(Base):
    __tablename__ = "pump_events"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    device_uuid = Column(String)
    timestamp = Column(DateTime, default=datetime.now())
