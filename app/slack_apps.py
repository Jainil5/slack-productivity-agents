import os
import re
import threading

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.services.agents.personal_agents.agent import run_agent

load_dotenv()


def markdown_to_slack(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<\2|\1>", text)
    return text


def personal_agent(query: str) -> str:
    return run_agent(query)


def knowledge_agent(query: str) -> str:
    try:
        response = requests.post(
            "http://127.0.0.1:8000/query",
            json={"query": query},
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "No response received.")

    except Exception as e:
        print(f"Knowledge Agent Error: {e}")
        return "Knowledge Agent is currently unavailable."


# ==================================================
# COMMON HANDLER
# ==================================================

def register_message_handler(app: App, agent_name: str, agent_fn):

    @app.event("message")
    def handle_message(event, say):

        if event.get("bot_id") or event.get("subtype"):
            return

        query = event.get("text", "").strip()

        if not query:
            return

        print("=" * 60)
        print(f"[{agent_name}] Incoming Query")
        print(query)
        print("=" * 60)

        try:
            response = agent_fn(query)
            say(markdown_to_slack(response))

        except Exception as e:
            print(f"{agent_name} Error: {e}")
            say(f"{agent_name} failed.")


# ==================================================
# PERSONAL AGENT
# ==================================================

personal_app = App(
    token=os.getenv("PA_BOT_TOKEN")
)

register_message_handler(
    personal_app,
    "Personal Agent",
    personal_agent,
)


# ==================================================
# KNOWLEDGE AGENT
# ==================================================

knowledge_app = App(
    token=os.getenv("KA_BOT_TOKEN")
)

register_message_handler(
    knowledge_app,
    "Knowledge Agent",
    knowledge_agent,
)


# ==================================================
# SOCKET MODE
# ==================================================

def start_socket(app: App, app_token: str, name: str):

    print(f"{name} connected.")

    SocketModeHandler(
        app,
        app_token,
    ).start()


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Starting Slack Agents")
    print("=" * 60)

    required = [
        "PA_BOT_TOKEN",
        "PA_APP_TOKEN",
        "KA_BOT_TOKEN",
        "KA_APP_TOKEN",
    ]

    for env in required:
        if not os.getenv(env):
            raise ValueError(f"{env} not found")

    threading.Thread(
        target=start_socket,
        args=(
            personal_app,
            os.getenv("PA_APP_TOKEN"),
            "Personal Agent",
        ),
        daemon=True,
    ).start()

    threading.Thread(
        target=start_socket,
        args=(
            knowledge_app,
            os.getenv("KA_APP_TOKEN"),
            "Knowledge Agent",
        ),
        daemon=True,
    ).start()

    print("All Slack agents are running...")
    threading.Event().wait()