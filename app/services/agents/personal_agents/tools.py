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


import json
from pathlib import Path
from datetime import datetime, timedelta

from langchain.tools import tool

ATTENDANCE_FILE = "app/data/attendance.json"

LEAVE_TYPES = ("sick", "casual", "paid")


def _load_data():
    with open(ATTENDANCE_FILE, "r") as f:
        return json.load(f)


def _save_data(data):
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def _normalize_date(date: str) -> str:
    """
    Converts relative dates into YYYY-MM-DD.
    """

    today = datetime.today()

    if not date:
        return today.strftime("%Y-%m-%d")

    date = date.strip().lower()

    if date == "today":
        return today.strftime("%Y-%m-%d")

    if date == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # Already in ISO format
    try:
        return datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        pass

    # Examples:
    # 5 July
    # 5 Jul
    # July 5
    # Jul 5

    current_year = today.year

    for fmt in (
        "%d %B",
        "%d %b",
        "%B %d",
        "%b %d",
    ):
        try:
            parsed = datetime.strptime(date.title(), fmt)
            parsed = parsed.replace(year=current_year)
            return parsed.strftime("%Y-%m-%d")
        except:
            pass

    # Unknown format
    return today.strftime("%Y-%m-%d")


@tool
def attendance_manager(
    action: str,
    leave_type: str = "",
    date: str = "",
) -> str:
    """
    Manage personal attendance.

    Actions:
    - apply
    - balance
    - history
    - summary

    Leave types:
    - sick
    - casual
    - paid
    """

    data = {
    "quota": {
        "sick": 6,
        "casual": 8,
        "paid": 12
    },
    "used": {
        "sick": 2,
        "casual": 0,
        "paid": 0
    },
    "history": [
        {
            "date": "2026-06-10",
            "type": "sick",
            "reason": "Fever"
        },
        {
            "date": "2026-07-12",
            "type": "sick"
        }
    ]
}

    action = action.lower().strip()

    if action == "apply":

        leave_type = leave_type.lower().strip()

        if leave_type not in LEAVE_TYPES:
            return (
                "Invalid leave type. "
                "Supported types: sick, casual, paid."
            )

        date = _normalize_date(date)

        remaining = (
            data["quota"][leave_type]
            - data["used"][leave_type]
        )

        if remaining <= 0:
            return f"No {leave_type} leaves remaining."

        data["used"][leave_type] += 1

        data["history"].append(
            {
                "date": date,
                "type": leave_type,
            }
        )

        _save_data(data)

        remaining -= 1

        return (
            f"{leave_type.title()} leave recorded for {date}.\n"
            f"Remaining {leave_type} leaves: {remaining}"
        )

    elif action == "balance":

        lines = ["Leave Balance\n"]

        for leave in LEAVE_TYPES:

            remaining = (
                data["quota"][leave]
                - data["used"][leave]
            )

            lines.append(
                f"{leave.title():<8}: "
                f"{remaining}/{data['quota'][leave]} remaining"
            )

        return "\n".join(lines)

    elif action == "history":

        history = sorted(
            data["history"],
            key=lambda x: x["date"],
            reverse=True,
        )

        if not history:
            return "No leave history found."

        lines = ["Leave History\n"]

        for item in history:
            lines.append(
                f"{item['date']}  •  {item['type'].title()}"
            )

        return "\n".join(lines)

    elif action == "summary":

        total_used = sum(data["used"].values())
        total_quota = sum(data["quota"].values())
        total_remaining = total_quota - total_used

        return (
            "Attendance Summary\n\n"
            f"Sick Leave   : {data['used']['sick']} / {data['quota']['sick']} used\n"
            f"Casual Leave : {data['used']['casual']} / {data['quota']['casual']} used\n"
            f"Paid Leave   : {data['used']['paid']} / {data['quota']['paid']} used\n\n"
            f"Total Used   : {total_used}\n"
            f"Remaining    : {total_remaining}"
        )

    return (
        "Unknown action.\n"
        "Valid actions are: apply, balance, history, summary."
    )

from langchain.tools import tool
from app.services.text_extraction import extract


@tool
def autotext_tool(query: str) -> str:
    """
    Use this tool when user wants to send message to someone or some group.

    Examples:
    - text backend team update the api
    - message frontend team about deploy api 
    
    """

    return extract(query,type="message")


# @tool
# def manage_event(query: str) -> str:
#     """
#     Use this tool when user wants to create or manage events like meetings.

#     Examples:
#     - create meeting with backend team at 2 PM
#     - schedule a meeting with frontend team at 2 PM
#     """
    
#     return extract(query,type="event")
    

