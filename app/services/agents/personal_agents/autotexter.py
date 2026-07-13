import time
import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.agents.personal_agents.slack_tools import SlackService

slack = SlackService()

extracted_details = [
    {
        "entity": "jainil",
        "personalized_message": "Send the requested project files via email."
    },
    {
        "entity": "backend team",
        "personalized_message": "Schedule a meeting with the backend team."
    }
]


# 1. LLM CONFIGURATION
llm = ChatOpenAI(
    model="gpt-oss:20b-cloud",                  
    base_url="http://localhost:11434/v1",
    api_key="ollama",                    
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}}
)


def send_autotext(user_input: str):
    """
    Parses an input string using the configured 'llm' variable,
    extracting entities and crafting precise, professional task statements.
    """
    prompt = PromptTemplate(
        template=(
            "You are an enterprise data extraction system. Analyze the raw user input, "
            "isolate individual entities (persons or teams), and convert the requested action "
            "into a concise, professional task description.\n\n"
            "CRITICAL WRITING RULES:\n"
            "1. Do NOT use greetings, names, or conversational pleasantries (e.g., avoid 'Hi', 'Hey', 'Please', 'Could you').\n"
            "2. Use direct, clear business phrasing.\n"
            "3. Output MUST be a valid JSON object containing a single key 'messages' with an array of objects.\n\n"
            "EXAMPLES:\n"
            "Input: text jainil to send files and riya to meet\n"
            "Output: {{\n"
            "  \"messages\": [\n"
            "    {{\"entity\": \"jainil\", \"personalized_message\": \"Transmit the requested project files via email.\"}},\n"
            "    {{\"entity\": \"riya\", \"personalized_message\": \"Coordinate an upcoming in-person meeting.\"}}\n"
            "  ]\n"
            "}}\n\n"
            "Input: {user_input}\n"
            "Output:"
        ),
        input_variables=["user_input"]
    )


    chain = prompt | llm | StrOutputParser()


    start_time = time.time()
    try:
        raw_json_string = chain.invoke({"user_input": user_input})
        end_time = time.time()
       
        data = json.loads(raw_json_string)
        result = slack.slack_autotext(data.get("messages", []))
        return result
       
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []





if __name__ == "__main__":
    query = "text dev and mann to give me update on project. And inform backend team to deploy the code"
   
    result = send_autotext(query)
   
    print(result)
