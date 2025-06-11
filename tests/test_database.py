"""
Unit tests for database operations.
"""
import os
import pytest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, WeatherRecord, LocationHistory, UserSetting
from src.database.operations import DatabaseOperations

@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def db_ops(db_session):
    """Create DatabaseOperations instance."""
    return DatabaseOperations(db_session)

class TestWeatherRecords:
    """Test weather record operations."""

    def test_save_weather_data(self, db_ops):
        """Test creating a new weather record."""
        record = db_ops.save_weather_data(
            location_name="New York",
            lat=40.7128,
            lon=-74.0060,
            temperature=20.5,
            feels_like=19.0,
            humidity=65,
            wind_speed=5.5,
            condition="Clear sky"
        )
        
        assert record.id is not None
        assert record.location_name == "New York"
        assert record.latitude == 40.7128
        assert record.longitude == -74.0060
        assert record.temperature == 20.5
        assert record.humidity == 65
        assert record.condition == "Clear sky"

    def test_get_weather_history(self, db_ops):
        """Test retrieving weather history."""
        # Add some test records
        for i in range(3):
            db_ops.save_weather_data(
                location_name="London",
                lat=51.5074,
                lon=-0.1278,
                temperature=18 + i,
                feels_like=17 + i,
                humidity=70,
                wind_speed=4.0,
                condition="Cloudy",
                date_range_start=date.today() - timedelta(days=i),
                date_range_end=date.today() - timedelta(days=i)
            )

        history = db_ops.get_weather_history("London")
        assert len(history) == 3
        assert all(r.location_name == "London" for r in history)
        assert history[0].temperature > history[1].temperature

    def test_update_weather_record(self, db_ops):
        """Test updating a weather record."""
        record = db_ops.save_weather_data(
            location_name="Paris",
            lat=48.8566,
            lon=2.3522,
            temperature=22.0,
            feels_like=21.0,
            humidity=68,
            wind_speed=3.5,
            condition="Partly cloudy"
        )
        
        updated = db_ops.update_weather_record(
            record.id,
            temperature=23.0,
            condition="Sunny"
        )
        
        assert updated.temperature == 23.0
        assert updated.condition == "Sunny"
        assert updated.location_name == "Paris"  # Unchanged field

    def test_delete_weather_record(self, db_ops):
        """Test deleting a weather record."""
        record = db_ops.save_weather_data(
            location_name="Berlin",
            lat=52.5200,
            lon=13.4050,
            temperature=19.0,
            feels_like=18.0,
            humidity=72,
            wind_speed=6.0,
            condition="Rain"
        )
        
        assert db_ops.delete_weather_record(record.id) is True
        history = db_ops.get_weather_history("Berlin")
        assert len(history) == 0

class TestLocationHistory:
    """Test location history operations."""

    def test_add_location_history(self, db_ops):
        """Test adding location search history."""
        history = db_ops.add_location_history(
            query="Tokyo",
            resolved_name="Tokyo, Japan",
            lat=35.6762,
            lon=139.6503
        )
        
        assert history.id is not None
        assert history.query == "Tokyo"
        assert history.resolved_name == "Tokyo, Japan"
        assert history.latitude == 35.6762
        assert history.longitude == 139.6503

    def test_get_location_history(self, db_ops):
        """Test retrieving location history."""
        locations = ["Rome", "Madrid", "Amsterdam"]
        for loc in locations:
            db_ops.add_location_history(query=loc)

        history = db_ops.get_location_history(limit=2)
        assert len(history) == 2
        assert history[0].query == "Amsterdam"  # Most recent first

    def test_clear_location_history(self, db_ops):
        """Test clearing location history."""
        db_ops.add_location_history(query="Sydney")
        db_ops.add_location_history(query="Melbourne")
        
        assert db_ops.clear_location_history() is True
        history = db_ops.get_location_history()
        assert len(history) == 0

class TestUserSettings:
    """Test user settings operations."""

    def test_set_and_get_setting(self, db_ops):
        """Test setting and retrieving user settings."""
        db_ops.set_setting("temperature_unit", "celsius")
        value = db_ops.get_setting("temperature_unit")
        assert value == "celsius"

    def test_update_setting(self, db_ops):
        """Test updating an existing setting."""
        db_ops.set_setting("theme", "light")
        db_ops.set_setting("theme", "dark")
        value = db_ops.get_setting("theme")
        assert value == "dark"

    def test_delete_setting(self, db_ops):
        """Test deleting a user setting."""
        db_ops.set_setting("language", "en")
        assert db_ops.delete_setting("language") is True
        assert db_ops.get_setting("language") is None