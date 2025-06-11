"""
Export Module - Handles data export to various formats (JSON, CSV, PDF).
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from ..core.weather_service import WeatherData, ForecastData

class DataExporter:
    """Handles export of weather data to various formats."""

    @staticmethod
    def export_to_json(
        weather: WeatherData,
        forecast: List[ForecastData],
        location: str,
        filepath: str
    ) -> None:
        """Export weather data to JSON format.
        
        Args:
            weather: Current weather data
            forecast: Forecast data list
            location: Location name
            filepath: Path to save JSON file
        """
        data = {
            "location": location,
            "exported_at": datetime.now().isoformat(),
            "current_weather": {
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "condition": weather.condition,
                "timestamp": weather.timestamp.isoformat()
            },
            "forecast": [
                {
                    "date": f.date.isoformat(),
                    "temp_min": f.temp_min,
                    "temp_max": f.temp_max,
                    "condition": f.condition,
                    "precipitation_prob": f.precipitation_prob
                }
                for f in forecast
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def export_to_csv(
        weather: WeatherData,
        forecast: List[ForecastData],
        location: str,
        filepath: str
    ) -> None:
        """Export weather data to CSV format.
        
        Args:
            weather: Current weather data
            forecast: Forecast data list
            location: Location name
            filepath: Path to save CSV file
        """
        rows = [
            ["Location:", location],
            ["Exported:", datetime.now().isoformat()],
            [],
            ["Current Weather"],
            ["Temperature:", f"{weather.temperature}°C"],
            ["Feels Like:", f"{weather.feels_like}°C"],
            ["Humidity:", f"{weather.humidity}%"],
            ["Wind Speed:", f"{weather.wind_speed} m/s"],
            ["Condition:", weather.condition],
            ["Timestamp:", weather.timestamp.isoformat()],
            [],
            ["5-Day Forecast"],
            ["Date", "Min Temp", "Max Temp", "Condition", "Precipitation Probability"]
        ]
        
        # Add forecast data
        for f in forecast:
            rows.append([
                f.date.strftime("%Y-%m-%d"),
                f"{f.temp_min}°C",
                f"{f.temp_max}°C",
                f.condition,
                f"{f.precipitation_prob * 100}%"
            ])
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    @staticmethod
    def export_to_pdf(
        weather: WeatherData,
        forecast: List[ForecastData],
        location: str,
        filepath: str
    ) -> None:
        """Export weather data to PDF format.
        
        Args:
            weather: Current weather data
            forecast: Forecast data list
            location: Location name
            filepath: Path to save PDF file
        """
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph(f"Weather Report - {location}", styles['Title']))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n", styles['Normal']))
        
        # Current weather table
        current_data = [
            ["Current Weather"],
            ["Temperature", f"{weather.temperature}°C"],
            ["Feels Like", f"{weather.feels_like}°C"],
            ["Humidity", f"{weather.humidity}%"],
            ["Wind Speed", f"{weather.wind_speed} m/s"],
            ["Condition", weather.condition],
            ["Timestamp", weather.timestamp.strftime("%Y-%m-%d %H:%M")]
        ]
        
        current_table = Table(current_data, colWidths=[200, 300])
        current_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(current_table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Forecast table
        forecast_data = [["Date", "Min Temp", "Max Temp", "Condition", "Precipitation"]]
        for f in forecast:
            forecast_data.append([
                f.date.strftime("%Y-%m-%d"),
                f"{f.temp_min}°C",
                f"{f.temp_max}°C",
                f.condition,
                f"{f.precipitation_prob * 100}%"
            ])
        
        forecast_table = Table(forecast_data, colWidths=[100, 80, 80, 160, 80])
        forecast_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph("5-Day Forecast", styles['Heading1']))
        elements.append(forecast_table)
        
        doc.build(elements)