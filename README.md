# Python Weather API client (`fetch_weather`)

Small, dependency-light Python wrapper around [WeatherAPI.com](https://www.weatherapi.com/) to fetch current weather by city.

## Install

### From GitHub

Once you push this repo to GitHub, other people can install it directly:

```bash
python -m pip install "git+https://github.com/headzoo/weather-api-python.git"
```

### From source (local dev)

```bash
python -m pip install -e ".[dev]"
```

## Usage

Set your API key:

```bash
export WEATHERAPI_KEY="..."
```

Call the function:

```python
from weather_api_python.weather import WeatherAPI

client = WeatherAPI(api_key="test")
data = fetch_weather("Austin")
print(data["temp_f"], data["condition"])
```

## Errors

Network/API problems raise `WeatherAPIError`:

```python
from weather_api_python.weather import WeatherAPIError, fetch_weather

try:
    fetch_weather("Austin")
except WeatherAPIError as e:
    print("Weather error:", e)
```

## Running Tests

To run the tests, you'll need [pytest](https://docs.pytest.org/), which is included if you install the dev dependencies:

```bash
pytest -m pytest
```