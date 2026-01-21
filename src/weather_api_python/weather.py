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


def fetch_weather(
    city: str,
    api_key: str | None = None,
    *,
    timeout: float = 10.0,
    client: httpx.Client | None = None,
) -> WeatherResult:
    """
    Fetch current weather for a given city using WeatherAPI.com.

    - **city**: City name (e.g. "Austin", "Paris", "Tokyo")
    - **api_key**: WeatherAPI key; defaults to env var WEATHERAPI_KEY
    - **timeout**: Request timeout (seconds)
    - **client**: Optional shared httpx.Client (useful for testing/reuse)

    Docs: https://www.weatherapi.com/docs/
    """
    city = (city or "").strip()
    if not city:
        raise ValueError("city must be a non-empty string")

    api_key = (api_key or os.getenv("WEATHERAPI_KEY") or "").strip()
    if not api_key:
        raise ValueError("WEATHERAPI_KEY is not set (or pass api_key=...)")

    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": "no"}

    close_client = False
    if client is None:
        client = httpx.Client(timeout=timeout)
        close_client = True

    try:
        resp = client.get(url, params=params)
    except httpx.HTTPError as e:
        raise WeatherAPIError(f"Network error calling WeatherAPI: {e}") from e
    finally:
        if close_client:
            client.close()

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
        "city": location.get("name") or city,
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
