"""
Database CRUD operations for the weather application.
"""
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, desc, cast, Date
from sqlalchemy.orm import Session

from .models import WeatherRecord, LocationHistory, UserSetting

class DatabaseOperations:
    """Handles all database CRUD operations."""

    def __init__(self, session: Session):
        """Initialize database operations with a session."""
        self.session = session

    def _commit_and_refresh(self, instance):
        """Helper method to commit changes and refresh instance."""
        try:
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except:
            self.session.rollback()
            raise

    # Weather Records Operations
    def save_weather_data(self, 
                         location_name: str,
                         lat: float,
                         lon: float,
                         temperature: float,
                         feels_like: float,
                         humidity: int,
                         wind_speed: float,
                         condition: str,
                         date_range_start: Optional[date] = None,
                         date_range_end: Optional[date] = None) -> WeatherRecord:
        """Create a new weather record."""
        record = WeatherRecord(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            temperature=temperature,
            feels_like=feels_like,
            humidity=humidity,
            wind_speed=wind_speed,
            condition=condition,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )
        self.session.add(record)
        return self._commit_and_refresh(record)

    def get_weather_history(self,
                          location_name: str,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> List[WeatherRecord]:
        """Query weather history for a location within date range."""
        try:
            query = self.session.query(WeatherRecord)
            query = query.filter(WeatherRecord.location_name == location_name)
            
            if start_date and end_date:
                # First try to match records with explicit date ranges
                query = query.filter(
                    and_(
                        WeatherRecord.date_range_start <= end_date,
                        WeatherRecord.date_range_end >= start_date
                    ) if WeatherRecord.date_range_start is not None 
                    else cast(WeatherRecord.timestamp, Date).between(start_date, end_date)
                )
            
            records = query.order_by(desc(WeatherRecord.timestamp)).all()
            print(f"Found {len(records)} records for {location_name}")  # Debug logging
            return records
            
        except Exception as e:
            self.session.rollback()
            print(f"Database error in get_weather_history: {str(e)}")  # Debug logging
            return []

    def update_weather_record(self, record_id: int, **updates) -> Optional[WeatherRecord]:
        """Update an existing weather record."""
        record = self.session.query(WeatherRecord).get(record_id)
        if record:
            for key, value in updates.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            return self._commit_and_refresh(record)
        return None

    def delete_weather_record(self, record_id: int) -> bool:
        """Delete a weather record."""
        try:
            record = self.session.query(WeatherRecord).get(record_id)
            if record:
                self.session.delete(record)
                self.session.commit()
                return True
            return False
        except:
            self.session.rollback()
            raise

    # Location History Operations
    def add_location_history(self,
                           query: str,
                           resolved_name: Optional[str] = None,
                           lat: Optional[float] = None,
                           lon: Optional[float] = None) -> LocationHistory:
        """Add a location search to history."""
        history = LocationHistory(
            query=query,
            resolved_name=resolved_name,
            latitude=lat,
            longitude=lon
        )
        self.session.add(history)
        return self._commit_and_refresh(history)

    def get_location_history(self, limit: int = 10) -> List[LocationHistory]:
        """Get recent location searches."""
        return self.session.query(LocationHistory)\
            .order_by(desc(LocationHistory.timestamp))\
            .limit(limit)\
            .all()

    def clear_location_history(self) -> bool:
        """Clear all location history."""
        self.session.query(LocationHistory).delete()
        self.session.commit()
        return True

    # User Settings Operations
    def set_setting(self, key: str, value: str) -> UserSetting:
        """Set or update a user setting."""
        setting = self.session.query(UserSetting)\
            .filter(UserSetting.setting_key == key)\
            .first()
            
        if setting:
            setting.setting_value = value
            setting.last_updated = datetime.utcnow()
        else:
            setting = UserSetting(
                setting_key=key,
                setting_value=value
            )
            self.session.add(setting)
            
        self.session.commit()
        return setting

    def get_setting(self, key: str) -> Optional[str]:
        """Get a user setting value."""
        setting = self.session.query(UserSetting)\
            .filter(UserSetting.setting_key == key)\
            .first()
        return setting.setting_value if setting else None

    def delete_setting(self, key: str) -> bool:
        """Delete a user setting."""
        setting = self.session.query(UserSetting)\
            .filter(UserSetting.setting_key == key)\
            .first()
        if setting:
            self.session.delete(setting)
            self.session.commit()
            return True
        return False