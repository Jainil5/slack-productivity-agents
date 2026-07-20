import os
import re
from difflib import SequenceMatcher
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()

client = WebClient(token=os.getenv("PA_BOT_TOKEN"))


def get_users():

    response = client.users_list()

    users = []

    for member in response["members"]:

        profile = member.get("profile", {})

        users.append(
            {
                "id": member["id"],
                "real_name": member.get("real_name", ""),
                "display_name": profile.get("display_name", ""),
                "username": member.get("name", ""),
            }
        )

    return users

def get_channels():

    response = client.conversations_list(
        types="public_channel,private_channel"
    )

    channels = []

    for channel in response["channels"]:

        channels.append(
            {
                "id": channel["id"],
                "name": channel["name"],
                "previous_names": channel.get("previous_names", []),
            }
        )

    return channels

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def score_match(query: str, candidate: str) -> float:

    query = normalize(query)
    candidate = normalize(candidate)

    if query == candidate:
        return 1.0

    if query in candidate:
        return 0.95

    query_words = set(query.split())
    candidate_words = set(candidate.split())

    if query_words.issubset(candidate_words):
        return 0.90

    return similarity(query, candidate)

def resolve_entity(entity: str):

    query = normalize(entity)

    best_score = 0
    best_match = None

    # Users

    for user in get_users():

        possible_names = [
            user.get("real_name", ""),
            user.get("display_name", ""),
            user.get("username", ""),
        ]

        for name in possible_names:

            if not name:
                continue

            score = score_match(query, name)

            if score > best_score:
                best_score = score
                best_match = {
                    "id": user["id"],
                    "type": "user",
                    "name":name
                }

    # Channels

    for channel in get_channels():

        possible_names = [
            channel.get("name", "")
        ] + channel.get("previous_names", [])

        for name in possible_names:

            if not name:
                continue

            score = score_match(query, name)

            if score > best_score:
                best_score = score
                best_match = {
                    "id": channel["id"],
                    "type": "channel",
                    "name":name
                }

    if best_score < 0.60:
        return None

    return best_match

def slack_autotext(entity: str, message: str):

    resolved_entity = resolve_entity(entity)

    if resolved_entity is None:
        return {
            "success": False,
            "message": f"Could not find '{entity}' in Slack."
        }

    slack_id = resolved_entity["id"]
    entity_type = resolved_entity["type"]
    name = resolved_entity["name"]

    try:

        response = client.chat_postMessage(
            channel=slack_id,
            text=message
        )

        return f"Message sent :{name} ({entity_type})."
        # return {
        #     "success": True,
        #     "id": slack_id,
        #     "type": entity_type,
        #     "name":name,
        #     "ts": response["ts"],
        # }

    except Exception as e:

        return f"Failed to send message to {name} ({entity_type}). Error in send_message_file: {e}"
        # return {
        #     "success": False,
        #     "message": str(e),
        # }

if __name__ == "__main__":

    print(
        slack_autotext(
            entity="Jainil",
            message="Hello Jainil."
        )
    )

    print(
        slack_autotext(
            entity="backend team",
            message="Please send today's standup updates."
        )
    )