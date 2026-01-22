from __future__ import annotations

import os
from typing import Any, TypedDict

import httpx


class WeatherAPIError(RuntimeError):
    """Raised when WeatherAPI.com returns an error or an unexpected response."""


class WeatherResult(TypedDict, total=False):
    city: str
    region: str | None
    country: str | None
    localtime: str | None
    temp_c: float | None
    temp_f: float | None
    condition: str | None
    humidity: int | None
    wind_mph: float | None
    wind_kph: float | None
    last_updated: str | None
    raw: dict[str, Any]

class WeatherAPI:
    def __init__(self, api_key: str, client: httpx.Client | None = None, timeout: float = 10.0):
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=timeout)

    def fetch_weather(
        self,
        location: str,
    ) -> WeatherResult:
        """
        Fetch current weather for a given city using WeatherAPI.com.

        - **location**: City name (e.g. "Austin", "Paris", "Tokyo") or zip code (e.g. "10001", "75001")

        Docs: https://www.weatherapi.com/docs/
        """
        location = (location or "").strip()
        if not location:
            raise ValueError("city must be a non-empty string")

        url = "https://api.weatherapi.com/v1/current.json"
        params = {"key": self.api_key, "q": location, "aqi": "no"}

        close_client = False
        if self.client is None:
            raise ValueError("client is required")

        try:
            resp = self.client.get(url, params=params)
        except httpx.HTTPError as e:
            raise WeatherAPIError(f"Network error calling WeatherAPI: {e}") from e
        finally:
            if close_client:
                self.client.close()

        # WeatherAPI returns useful details in JSON body on error
        try:
            data: Any = resp.json()
        except ValueError:
            data = None

        if resp.is_error:
            msg = None
            if isinstance(data, dict):
                msg = (data.get("error") or {}).get("message")
            raise WeatherAPIError(f"WeatherAPI error {resp.status_code}: {msg or resp.text}")

        if isinstance(data, dict) and "error" in data:
            # Defensive: in case WeatherAPI ever returns 200 with an error payload.
            raise WeatherAPIError(
                (data["error"] or {}).get("message") or "Unknown WeatherAPI error"
            )

        if not isinstance(data, dict) or "current" not in data:
            raise WeatherAPIError("Unexpected WeatherAPI response shape")

        location = data.get("location") or {}
        current = data.get("current") or {}
        condition = current.get("condition") or {}

        return {
            "city": location.get("name") or location,
            "region": location.get("region"),
            "country": location.get("country"),
            "localtime": location.get("localtime"),
            "temp_c": current.get("temp_c"),
            "temp_f": current.get("temp_f"),
            "condition": condition.get("text"),
            "humidity": current.get("humidity"),
            "wind_mph": current.get("wind_mph"),
            "wind_kph": current.get("wind_kph"),
            "last_updated": current.get("last_updated"),
            "raw": data,
        }
