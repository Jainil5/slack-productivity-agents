# test_query.py

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/query"


def query_api(query: str, session_id: str = "test-user"):
    payload = {
        "query": query,
        "session_id": session_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        print("\nStatus Code:", response.status_code)
        print("\nResponse:")
        print(json.dumps(response.json(), indent=4))

        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(response.text)

    except requests.exceptions.ConnectionError:
        print("Could not connect to the FastAPI server.")
        print("Make sure it is running on http://127.0.0.1:8000")

    except requests.exceptions.Timeout:
        print("Request timed out.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    while True:
        user_query = input("\nYou: ")

        if user_query.lower() in {"exit", "quit"}:
            break

        query_api(user_query)