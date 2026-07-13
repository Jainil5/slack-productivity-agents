import uuid
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# from test.tools import (
#     search_tool,
#     get_weather,
# )

load_dotenv()
# MEMORY

memory = InMemorySaver()

# SYSTEM PROMPT

SYSTEM_PROMPT = """
You are Agent.

You are an intelligent workplace assistant.

Responsibilities:

- Answer questions.
- Help with Slack workflows.
- Help with scheduling.
- Help with emails.
- Help with uploaded files.
- Use tools whenever required.

Tool Rules:

1. Search Tool
- Use for factual and current information.

2. Weather Tool
- Use only for weather questions.

General Rules:

- Never hallucinate.
- Be concise.
- Use tools whenever necessary.
"""

# ==================================================
# AGENT
# ==================================================

agent = create_agent(
    model="ollama:gpt-oss:20b-cloud",
    # tools=[
    #     search_tool,
    #     get_weather,
    # ],
    checkpointer=memory,
    system_prompt=SYSTEM_PROMPT,
)

# SESSION CONFIG

thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        "thread_id": thread_id,
        "user_id": "slack_user",
    }
}

print(
    f"\nConversation Thread: {thread_id}\n"
)

# AGENT FUNCTION

def run_agent(
    message: str,
    user_id: str = "",
    user_name: str = "",
    channel_id: str = "",
    channel_name: str = "",
    uploaded_files: list | None = None,
):

    if uploaded_files is None:
        uploaded_files = []

    prompt = f"""
    User Information
    ----------------
    User Name: {user_name}
    User ID: {user_id}

    Channel Information
    -------------------
    Channel Name: {channel_name}
    Channel ID: {channel_id}

    Uploaded Files
    --------------
    {uploaded_files}

    User Message
    ------------
    {message}
    """

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        },
        config=config,
    )

    return result[
        "messages"
    ][-1].content


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TS Agent")
    print("=" * 60)

    while True:

        query = input(
            "\nYou: "
        )

        if query.lower() in [
            "exit",
            "quit",
            "q",
        ]:
            break

        try:

            response = run_agent(
                message=query,
                user_name="Local User",
                channel_name="Terminal",
            )

            print(
                f"\nAssistant:\n{response}"
            )

        except Exception as e:

            print(
                f"\nError: {e}"
            )