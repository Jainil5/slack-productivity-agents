import json
import pandas as pd
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from app.services.slack_tools import slack_autotext

load_dotenv()


llm = ChatOllama(
    model="gpt-oss:20b-cloud",
    temperature=0,
)


SYSTEM_PROMPT = """
You are a backend software engineer.

An anomaly detection engine has already analyzed an API request.

DO NOT determine whether the request is normal or abnormal.
DO NOT invent new reasons.

Your only responsibility is to explain the supplied anomaly to the engineering team.

You will receive:

- Behaviour
- Reasons
- API Log

If behaviour is "abnormal":

Write a professional engineering notification.

Start with:

Hello Team,

Then state that an abnormal API request has been detected.

Explain the supplied reasons in simple engineering language.

Examples:

HIGH_LATENCY
→ The request took significantly longer than expected.


REQUEST_FAILED - 500
→ The request failed with HTTP 500.


REQUEST_FAILED - 503
→ The service was unavailable and returned HTTP 503.


After that include:


Log Details


- Request ID
- Service
- Endpoint
- HTTP Method
- Query (if available)
- HTTP Status
- Latency


Finish with one sentence suggesting what the engineering team should investigate.


Keep the message concise and professional.


If behaviour is "normal", simply state that the request follows historical behaviour and no action is required.
"""


def generate_incident_message(behaviour: str,reasons: list[str],log: dict) -> str:


    prompt = f"""
    Behaviour:
    {behaviour}


    Reasons:
    {json.dumps(reasons, indent=2)}


    API Log:
    {json.dumps(log, indent=2)}


    Generate the engineering notification.
    """


    response = llm.invoke(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
   
    # print(response.content)

    slack_autotext("backend-team",response.content)


def analyze_log(
    csv_path: str,
    new_log: dict,
    endpoint_column: str = "endpoint",
    latency_column: str = "latency_ms",
    status_column: str = "status_code",
    history_size: int = 100,
    save_log: bool = True,
):


    df = pd.read_csv(csv_path)
    history_df = df.copy()
    if save_log==True:
        df = pd.concat(
            [
                df,
                pd.DataFrame([new_log]),
            ],
            ignore_index=True,
        )

        df.to_csv(
            csv_path,
            index=False,
        )        

    history = (
        history_df[
            history_df[endpoint_column] == new_log[endpoint_column]
        ]
        .tail(history_size)
        .copy()
    )

    if history.empty:
        raise ValueError(
            f"No historical data found for endpoint '{new_log[endpoint_column]}'."
        )

    median_latency = float(
        history[latency_column].median()
    )

    p95_latency = float(
        history[latency_column].quantile(0.95)
    )

    current_latency = float(
        new_log[latency_column]
    )

    current_status = int(
        new_log[status_column]
    )

    behaviour = "normal"
    reasons = []
    if (
        current_latency > p95_latency
        or current_latency > (median_latency * 3)
    ):
        behaviour = "abnormal"
        reasons.append("HIGH_LATENCY")

    if current_status not in (200,):
        behaviour = "abnormal"
        reasons.append(
            f"REQUEST_FAILED - HTTP {current_status}"
        )
    if behaviour=="abnormal":
        generate_incident_message(behaviour,reasons,new_log)

    return {
        "behaviour": behaviour,
        "reasons": reasons,
        "log": new_log,
    }


if __name__ == "__main__":
    new_log = {
        "request_id": "REQ-10291",
        "timestamp": "2026-07-16T10:01:05",
        "service": "SearchService",
        "endpoint": "/query",
        "method": "POST",
        "query": "camera calibration",
        "status_code": 200,
        "latency_ms": 185,
        "retry_count": 0,
    }

    new_log2 = {
        "request_id": "REQ-10542",
        "timestamp": "2026-07-16T10:42:31Z",
        "service": "SearchService",
        "endpoint": "/login",
        "method": "POST",
        "query": "user login",
        "status_code": 400,
        "latency_ms": 180,
        "retry_count": 0
        }


    analyze_log(
        new_log=new_log2,
        csv_path="app/data/api_logs.csv",
        save_log=False
    )









