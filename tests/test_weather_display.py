"""
Test for WeatherDisplay table population and blank state.
"""
import pytest
from PyQt5.QtWidgets import QApplication
from src.ui.widgets.weather_display import WeatherDisplay
from src.core.weather_service import WeatherData
from datetime import datetime
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_history_table_blank_on_no_location(app):
    wd = WeatherDisplay()
    wd._current_location = None
    wd._load_history()
    assert wd.history_table.rowCount() == 0

def test_history_table_populates_on_location(app, monkeypatch):
    wd = WeatherDisplay()
    wd._current_location = "Test City"
    wd.start_date.setDate(datetime(2024, 1, 1).date())
    wd.end_date.setDate(datetime(2024, 1, 2).date())
    class FakeRecord:
        def __init__(self):
            self.timestamp = datetime(2024, 1, 1, 12, 0)
            self.temperature = 20.0
            self.feels_like = 19.0
            self.humidity = 50
            self.wind_speed = 3.0
            self.condition = "Clear"
    monkeypatch.setattr("src.ui.widgets.weather_display.db.get_weather_history", lambda *a, **kw: [FakeRecord()])
    wd._load_history()
    assert wd.history_table.rowCount() == 1
