from click import prompt
import json
import time
from typing import List
from pydantic import BaseModel, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.slack_tools import slack_autotext

class Message(BaseModel):
    entity: str
    personalized_message: str

class Messages(BaseModel):
    messages: List[Message]


llm = ChatOpenAI(
    model="gpt-oss:20b-cloud",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
)

message_prompt = PromptTemplate(
        template=(
            "You are an enterprise data extraction system. Analyze the raw user input, "
            "isolate individual entities (persons or teams), and convert the requested action "
            "into a concise, professional task description.\n\n"
            "CRITICAL WRITING RULES:\n"
            "1. Do NOT use greetings, names, or conversational pleasantries "
            "(e.g., avoid 'Hi', 'Hey', 'Please', 'Could you').\n"
            "2. Use direct, clear business phrasing.\n"
            "3. Output MUST be a valid JSON object containing a single key "
            "'messages' with an array of objects.\n\n"
            "EXAMPLES:\n"
            "Input: text jainil to send files and riya to meet\n"
            "Output: {{\n"
            '  "messages": [\n'
            '    {{"entity": "jainil", "personalized_message": '
            '"Transmit the requested project files via email."}},\n'
            '    {{"entity": "riya", "personalized_message": '
            '"Coordinate an upcoming in-person meeting."}}\n'
            "  ]\n"
            "}}\n\n"
            "Input: {user_input}\n"
            "Output:"
        ),
        input_variables=["user_input"],
    )

def extract(user_input: str, type: str = "message"):


    if type=="message":
        prompt = message_prompt
    # elif type=="event":
    #     prompt = event_prompt

    chain = prompt | llm | StrOutputParser()

    try:

        raw_json_string = chain.invoke({"user_input": user_input})

        data = json.loads(raw_json_string)

        validated_response = Messages.model_validate(data)

        slack_messages = [
            message.model_dump()
            for message in validated_response.messages
        ]

        extracted_details = slack_messages

        for item in extracted_details:
            entity = item.get("entity")
            message = item.get("personalized_message")

            response = slack_autotext(entity,message)
        
            return response


    except json.JSONDecodeError:
        print("Invalid JSON returned by the model.")
        return []

    except ValidationError as e:
        print(f"Pydantic Validation Error:\n{e}")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    query = "Text backend team to schedule a meeting at 2 PM"

    result = extract(query)

    print(result)