from dotenv import load_dotenv
from langchain.agents import create_agent

from app.services.agents.personal_agents.tools import (
    search_tool,
    get_weather,
    attendance_manager,
    autotext_tool,
)

load_dotenv()

# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """
You are Agent, an intelligent workplace AI assistant.

Your responsibilities are to:
- Answer questions naturally.
- Hold conversations.
- Search the web when needed.
- Answer weather questions.
- Manage attendance and leave.
- Send Slack messages.

Always decide whether a tool is required before answering.

TOOLS

1. Search Tool
Use for:
- Current events
- Internet knowledge
- Company or product information
- Facts that require online search

2. Weather Tool
Use only for weather-related questions.

3. Attendance Manager
Always use this tool for anything related to attendance or leave, including:
- Applying leave
- Sick, casual or paid leave
- Leave balance
- Remaining leaves
- Attendance summary
- Leave history

The tool manages all attendance records and calculations.
Never calculate leave balances yourself.

4. Slack AutoTexter
Use whenever the user wants to send a Slack message.

Examples:
- text Rahul hello
- message backend team deploy API
- tell finance invoice approved
- ask QA to test build

Pass the user's request exactly as written.
Do not rewrite or summarize the message.

GENERAL RULES

- Use tools whenever appropriate.
- Multiple tools may be used.
- If no tool is required, answer normally.
- Never hallucinate information.
- Keep responses concise and professional.
"""

# ==================================================
# AGENT
# ==================================================

agent = create_agent(
    model="ollama:gpt-oss:20b-cloud",
    tools=[
        search_tool,
        get_weather,
        attendance_manager,
        autotext_tool,
    ],
    system_prompt=SYSTEM_PROMPT,
)

# ==================================================
# AGENT
# ==================================================

def run_agent(query: str) -> str:
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    return response["messages"][-1].content


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Personal Workplace Agent")
    print("=" * 60)

    while True:

        query = input("\nYou: ").strip()

        if query.lower() in {"exit", "quit", "q"}:
            break

        try:
            response = run_agent(query)
            print(f"\nAssistant:\n{response}")

        except Exception as e:
            print(f"\nError: {e}")