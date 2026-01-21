import httpx
import pytest

from weather_api_python.weather import WeatherAPIError, fetch_weather


def test_fetch_weather_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.weatherapi.com"
        assert request.url.path == "/v1/current.json"
        assert request.url.params["q"] == "Austin"
        return httpx.Response(
            200,
            json={
                "location": {"name": "Austin", "region": "Texas", "country": "USA"},
                "current": {
                    "temp_c": 20.0,
                    "temp_f": 68.0,
                    "humidity": 55,
                    "wind_mph": 4.0,
                    "wind_kph": 6.4,
                    "last_updated": "2026-01-21 12:00",
                    "condition": {"text": "Clear"},
                },
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    data = fetch_weather("Austin", api_key="test", client=client)
    assert data["city"] == "Austin"
    assert data["temp_f"] == 68.0
    assert data["condition"] == "Clear"


def test_fetch_weather_http_error_raises_weather_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(WeatherAPIError) as exc:
        fetch_weather("Austin", api_key="bad", client=client)
    assert "Invalid API key" in str(exc.value)
