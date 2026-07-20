import json
import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from slack_sdk import WebClient

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("SLACK_REDIRECT_URL")

USER_FILE = "users.json"

app = FastAPI()


def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def save_user_token(user_id, token, username, team_id):
    users = load_users()

    users[user_id] = {
        "username": username,
        "token": token,
        "team_id": team_id
    }

    save_users(users)


def exchange_code_for_token(code):
    response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URL,
        },
    )

    return response.json()


@app.get("/")
def home():
    return {
        "message": "Personal Agent OAuth Server Running"
    }


@app.get("/slack/login")
def slack_login():
    login_url = (
        "https://slack.com/oauth/v2/authorize"
        f"?client_id={CLIENT_ID}"
        "&user_scope=chat:write,im:write,users:read"
        f"&redirect_uri={REDIRECT_URL}"
    )

    return RedirectResponse(login_url)


@app.get("/slack/callback")
def slack_callback(code: str):

    data = exchange_code_for_token(code)

    if not data.get("ok"):
        return data

    authed_user = data["authed_user"]

    user_id = authed_user["id"]
    token = authed_user["access_token"]

    client = WebClient(token=token)

    user_info = client.auth_test()

    username = user_info["user"]
    team_id = user_info["team_id"]

    save_user_token(
        user_id=user_id,
        token=token,
        username=username,
        team_id=team_id,
    )

    return HTMLResponse(
        f"""
        <h2>Successfully Connected!</h2>

        <p>User ID : {user_id}</p>
        <p>Username : {username}</p>
        <p>Team ID : {team_id}</p>

        <h3>Your Personal Agent is ready.</h3>
        """
    )


@app.get("/users")
def get_users():
    return load_users()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )