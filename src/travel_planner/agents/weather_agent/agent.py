import aiohttp
from typing import Dict
from google.adk.tools import FunctionTool
from google.adk.agents import Agent

weather_descriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def get_weather(city: str, start_date: str, end_date: str) -> Dict:
    """
    Get weather forecast for a city between start_date and end_date.

    Args:
        city: City name (e.g., "London", "New York")
        start_date: Start date in format "YYYY-MM-DD"
        end_date: End date in format "YYYY-MM-DD"

    Returns:
        Dictionary containing weather forecast data
    """
    # Using Open-Meteo API (free, no API key required)

    # First, geocode the city to get coordinates
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"

    async with aiohttp.ClientSession() as session:
        # Get city coordinates
        async with session.get(geocoding_url) as response:
            geo_data = await response.json()

            if not geo_data.get("results"):
                return {"error": f"City '{city}' not found"}

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]

        # Get weather forecast
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,sunset,apparent_temperature_mean"
            f"&start_date={start_date}&end_date={end_date}"
            f"&timezone=auto"
        )

        async with session.get(weather_url) as response:
            weather_data = await response.json()

            if "error" in weather_data:
                return {"error": weather_data["error"]}

            # Format the response
            daily = weather_data["daily"]
            forecast = []

            for i in range(len(daily["time"])):
                forecast.append(
                    {
                        "date": daily["time"][i],
                        "temp_max": daily["temperature_2m_max"][i],
                        "temp_min": daily["temperature_2m_min"][i],
                        "apparent_temperature_mean": daily["apparent_temperature_mean"][
                            i
                        ],
                        "precipitation": daily["precipitation_sum"][i],
                        "weather_description": weather_descriptions.get(
                            daily["weathercode"][i], "Unknown"
                        ),
                        "sunset": daily["sunset"][i],
                    }
                )

            return {"forecast": forecast}


def get_weather_agent():
    instructions = """
  You are a weather forecast agent. Given a destination and date range, provide the weather forecast using the get_weather tool.
  If you are unable to discern the exact weather from the tool, provide a general expectation based on typical weather patterns for that location and time of year.
  """
    weather_agent = Agent(
        model="gemini-2.5-flash",
        name="weather_agent",
        description="An agent that gets weather forecasts.",
        instruction=instructions,
        tools=[FunctionTool(func=get_weather)],
        output_key="weather_data",
    )
    return weather_agent
