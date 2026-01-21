"""
weather_api_python

Public API:
- fetch_weather(): fetch current weather by city (WeatherAPI.com)
"""

from .weather import WeatherAPIError, WeatherResult, fetch_weather

__all__ = ["WeatherAPIError", "WeatherResult", "fetch_weather"]
