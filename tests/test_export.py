"""
Tests for data export functionality
"""
import json
import os
from datetime import datetime
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from src.core.weather_service import WeatherData, ForecastData
from src.utils.export import DataExporter

@pytest.fixture
def sample_weather_data():
    """Create sample weather data for testing."""
    return WeatherData(
        temperature=20.5,
        feels_like=21.0,
        humidity=65,
        wind_speed=5.2,
        condition="Clear sky",
        icon="01d",
        timestamp=datetime(2024, 1, 1, 12, 0),
        location_name="Test City",
        latitude=40.0,
        longitude=-74.0
    )

@pytest.fixture
def sample_forecast_data():
    """Create sample forecast data for testing."""
    return [
        ForecastData(
            date=datetime(2024, 1, 1 + i, 12, 0),
            temp_min=18.0 + i,
            temp_max=25.0 + i,
            condition="Clear sky",
            icon="01d",
            precipitation_prob=0.1
        )
        for i in range(5)
    ]

def test_export_to_json(tmp_path, sample_weather_data, sample_forecast_data):
    """Test JSON export functionality."""
    # Setup test file path
    filepath = tmp_path / "weather_data.json"
    
    # Export data
    DataExporter.export_to_json(
        sample_weather_data,
        sample_forecast_data,
        "Test City",
        str(filepath)
    )
    
    # Verify file exists and content
    assert filepath.exists()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data["location"] == "Test City"
    assert data["current_weather"]["temperature"] == 20.5
    assert len(data["forecast"]) == 5
    assert isinstance(data["exported_at"], str)

def test_export_to_csv(tmp_path, sample_weather_data, sample_forecast_data):
    """Test CSV export functionality."""
    # Setup test file path
    filepath = tmp_path / "weather_data.csv"
    
    # Export data
    DataExporter.export_to_csv(
        sample_weather_data,
        sample_forecast_data,
        "Test City",
        str(filepath)
    )
    
    # Verify file exists and basic content
    assert filepath.exists()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check key data points
    assert "Test City" in content
    assert "20.5°C" in content
    assert "Clear sky" in content
    assert all(f"2024-01-0{i+1}" in content for i in range(5))

def test_export_to_pdf(tmp_path, sample_weather_data, sample_forecast_data):
    """Test PDF export functionality."""
    # Setup test file path
    filepath = tmp_path / "weather_data.pdf"
    
    # Export data
    DataExporter.export_to_pdf(
        sample_weather_data,
        sample_forecast_data,
        "Test City",
        str(filepath)
    )
    
    # Verify file exists and is a valid PDF
    assert filepath.exists()
    assert filepath.stat().st_size > 0
    
    # Basic validation of PDF header bytes
    with open(filepath, 'rb') as f:
        header = f.read(4)
        assert header == b'%PDF'

def test_export_with_invalid_path(sample_weather_data, sample_forecast_data):
    """Test handling of invalid export paths."""
    invalid_path = "/nonexistent/directory/file.json"
    
    with pytest.raises(Exception):
        DataExporter.export_to_json(
            sample_weather_data,
            sample_forecast_data,
            "Test City",
            invalid_path
        )