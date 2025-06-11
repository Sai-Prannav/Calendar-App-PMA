"""
Test WeatherEditDialog for dict/object input and None handling.
"""
import pytest
from PyQt5.QtWidgets import QApplication
from src.ui.dialogs.weather_edit_dialog import WeatherEditDialog
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_edit_dialog_handles_dict_with_none(app):
    record = {
        'temperature': None,
        'feels_like': None,
        'humidity': None,
        'wind_speed': None,
        'condition': None
    }
    dialog = WeatherEditDialog(record, None)
    assert dialog.temp_input.value() == 0.0
    assert dialog.feels_input.value() == 0.0
    assert dialog.humidity_input.value() == 0
    assert dialog.wind_input.value() == 0.0
    assert dialog.condition_input.text() == ""

def test_edit_dialog_handles_object_with_none(app):
    class Dummy:
        temperature = None
        feels_like = None
        humidity = None
        wind_speed = None
        condition = None
    dialog = WeatherEditDialog(Dummy(), None)
    assert dialog.temp_input.value() == 0.0
    assert dialog.feels_input.value() == 0.0
    assert dialog.humidity_input.value() == 0
    assert dialog.wind_input.value() == 0.0
    assert dialog.condition_input.text() == ""
