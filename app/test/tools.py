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
from datetime import datetime
from langchain.tools import tool

DB_PATH = Path(__file__).parent / "attendance_db.json"

DEFAULT_QUOTA = {
    "sick": 6,
    "casual": 8,
    "paid": 12,
}


def load_db():
    if not DB_PATH.exists():
        DB_PATH.write_text("{}")
    return json.loads(DB_PATH.read_text())


def save_db(db):
    DB_PATH.write_text(json.dumps(db, indent=4))


@tool
def attendance_manager(
    username: str,
    action: str,
    leave_type: str = "",
    date: str = "",
    reason: str = "",
) -> str:
    """
    Manage employee attendance.

    Actions:
    - apply
    - balance
    - history
    - summary
    """

    db = load_db()

    if username not in db:
        db[username] = {
            "quota": DEFAULT_QUOTA.copy(),
            "used": {
                "sick": 0,
                "casual": 0,
                "paid": 0,
            },
            "history": [],
        }

    employee = db[username]

    action = action.lower()

    if action == "apply":

        leave_type = leave_type.lower()

        if leave_type not in employee["quota"]:
            return f"Unknown leave type: {leave_type}"

        if not date:
            date = datetime.today().strftime("%Y-%m-%d")

        employee["used"][leave_type] += 1

        employee["history"].append(
            {
                "date": date,
                "type": leave_type,
                "reason": reason or "Not provided",
            }
        )

        save_db(db)

        remaining = (
            employee["quota"][leave_type]
            - employee["used"][leave_type]
        )

        return (
            f"{leave_type.title()} leave applied.\n"
            f"Remaining {leave_type} leaves: {remaining}"
        )

    elif action == "balance":

        msg = []

        for leave in employee["quota"]:

            remaining = (
                employee["quota"][leave]
                - employee["used"][leave]
            )

            msg.append(
                f"{leave.title()}: {remaining}/{employee['quota'][leave]}"
            )

        return "\n".join(msg)

    elif action == "history":

        history = employee["history"]

        if not history:
            return "No leave history."

        lines = []

        for h in history:
            lines.append(
                f"{h['date']} | {h['type'].title()} | {h['reason']}"
            )

        return "\n".join(lines)

    elif action == "summary":

        lines = []

        total_used = 0

        for leave in employee["quota"]:

            used = employee["used"][leave]
            total = employee["quota"][leave]

            total_used += used

            lines.append(
                f"{leave.title()}: Used {used} / {total}"
            )

        lines.append(f"\nTotal Leaves Used: {total_used}")

        return "\n".join(lines)

    return "Unknown action."





