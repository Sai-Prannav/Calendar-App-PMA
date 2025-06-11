"""
Database package initialization.
"""
from .models import WeatherRecord, LocationHistory, UserSetting, init_db
from .operations import DatabaseOperations

__all__ = [
    'WeatherRecord',
    'LocationHistory', 
    'UserSetting',
    'DatabaseOperations',
    'init_db',
]

# Initialize database connection and session maker
engine, Session = init_db()

# Create a database operations instance
db = DatabaseOperations(Session())