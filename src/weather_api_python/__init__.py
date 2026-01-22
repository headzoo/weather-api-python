"""
weather_api_python

Public API:
- WeatherAPI.fetch_weather(): fetch current weather by city (WeatherAPI.com)
"""

from .weather import WeatherAPIError, WeatherResult, WeatherAPI

__all__ = ["WeatherAPIError", "WeatherResult", "WeatherAPI"]
