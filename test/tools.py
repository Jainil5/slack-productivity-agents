from langchain.tools import tool
import requests
from datetime import datetime
from pathlib import Path
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# Weather Tool


@tool
def get_weather(location: str) -> str:
    """
    Get the current weather for a given location.
    """


    try:
        response = requests.get(
            f"https://wttr.in/{location}?format=j1",
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()
        current = data["current_condition"][0]


        return (
            f"Weather in {location}\n"
            f"Temperature : {current['temp_C']}°C\n"
            f"Feels Like  : {current['FeelsLikeC']}°C\n"
            f"Humidity    : {current['humidity']}%\n"
            f"Wind Speed  : {current['windspeedKmph']} km/h\n"
            f"Condition   : {current['weatherDesc'][0]['value']}"
        )


    except Exception as e:
        return f"Unable to fetch weather information.\nError: {e}"


_search = DuckDuckGoSearchAPIWrapper()

@tool
def search_tool(query: str) -> str:
    """
    Search the web for information.
    """
    try:
        return _search.run(query)


    except Exception as e:
        return f"Search failed: {e}"







