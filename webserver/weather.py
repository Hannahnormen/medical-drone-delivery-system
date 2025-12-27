import requests

_WEATHER_URL = "http://api.weatherapi.com/v1/current.json"

def get_current_weather(city: str, api_key: str):
    """
    Fetch the current weather for `city` from WeatherAPI.
    Returns a dict with:
      'description': str,
      'temp_c': float,
      'wind_kph': float,
      'is_raining': bool
    Raises RuntimeError on any failure.
    """
    params = {"key": api_key, "q": city}
    resp = requests.get(_WEATHER_URL, params=params, timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"Weather API error: {resp.text}")

    data = resp.json()
    if "current" not in data:
        raise RuntimeError(f"Unexpected response: {data}")

    cond = data["current"]["condition"]["text"]
    temp = data["current"]["temp_c"]
    wind = data["current"]["wind_kph"]
    is_raining = "rain" in cond.lower()

    return {
        "description": cond,
        "temp_c": temp,
        "wind_kph": wind,
        "is_raining": is_raining
    }