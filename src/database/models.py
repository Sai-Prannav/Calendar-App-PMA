"""
Database models for the weather application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class WeatherRecord(Base):
    """Model for storing weather records."""
    __tablename__ = 'weather_records'

    id = Column(Integer, primary_key=True)
    location_name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Integer)
    wind_speed = Column(Float)
    condition = Column(String)
    date_range_start = Column(Date)
    date_range_end = Column(Date)

class LocationHistory(Base):
    """Model for storing location search history."""
    __tablename__ = 'location_history'

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    resolved_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserSetting(Base):
    """Model for storing user settings."""
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Database initialization function
def init_db(db_path: str = 'weather_app.db'):
    """Initialize the database and create tables."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session