import json
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import re
from difflib import get_close_matches
from typing import List, Dict

class SlackService:
    CACHE_FILE = "app/data/slack_workspace.json"

    def __init__(self):
        load_dotenv()

        self.bot_token = os.getenv("SLACK_BOT_TOKEN")

        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN not found in .env")

        self.client = WebClient(token=self.bot_token)

        self.workspace = {
            "users": [],
            "channels": []
        }

        self.lookup = {}

        self.load_cache()

    # Refresh Workspace

    def refresh_workspace(self):
        users = []
        channels = []

        cursor = None

        while True:

            response = self.client.users_list(cursor=cursor)

            for member in response["members"]:

                if member.get("deleted"):
                    continue

                profile = member.get("profile", {})

                users.append({
                    "id": member["id"],
                    "real_name": member.get("real_name", ""),
                    "display_name": profile.get("display_name", ""),
                    "username": member.get("name", ""),
                    "email": profile.get("email", "")
                })

            cursor = response.get("response_metadata", {}).get("next_cursor")

            if not cursor:
                break

        # ---------------- Channels ----------------

        cursor = None

        while True:

            response = self.client.conversations_list(
                types="public_channel,private_channel",
                limit=1000,
                cursor=cursor
            )

            for channel in response["channels"]:

                channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "previous_names": channel.get("previous_names", [])
                })

            cursor = response.get("response_metadata", {}).get("next_cursor")

            if not cursor:
                break

        self.workspace = {
            "users": users,
            "channels": channels
        }

        self.build_lookup()

        self.save_cache()

        print("Workspace refreshed.")

    # ============================================================
    # Cache
    # ============================================================

    def save_cache(self):

        with open(self.CACHE_FILE, "w") as f:
            json.dump(self.workspace, f, indent=4)

    def load_cache(self):

        if os.path.exists(self.CACHE_FILE):

            with open(self.CACHE_FILE, "r") as f:
                self.workspace = json.load(f)

            self.build_lookup()

        else:

            self.refresh_workspace()

    # ============================================================
    # Lookup
    # ============================================================

    @staticmethod
    def normalize(text):

        return (
            text.lower()
            .replace("#", "")
            .replace("-", " ")
            .replace("_", " ")
            .strip()
        )

    def build_lookup(self):

        self.lookup = {}

        # Users
        for user in self.workspace["users"]:

            values = [
                user["real_name"],
                user["display_name"],
                user["username"],
                user["email"]
            ]

            for value in values:

                if value:
                    self.lookup[self.normalize(value)] = user["id"]

        # Channels
        for channel in self.workspace["channels"]:

            self.lookup[self.normalize(channel["name"])] = channel["id"]

            for old in channel["previous_names"]:
                self.lookup[self.normalize(old)] = channel["id"]

    # Resolve Entity

    def resolve_entity(self, entity):

        return self.lookup.get(self.normalize(entity))

    def resolve_entity(self, entity):

        entity = self.normalize(entity)

        if entity in self.lookup:
            return self.lookup[entity]

        # 2. Regex / Partial Match

        for user in self.get_users():

            candidates = [
                user.get("real_name", ""),
                user.get("display_name", ""),
                user.get("username", ""),
                user.get("email", "")
            ]

            for value in candidates:

                if not value:
                    continue

                value = self.normalize(value)

                if (
                    re.search(rf"\b{re.escape(entity)}\b", value)
                    or entity in value
                    or value in entity
                ):
                    return user["id"]

        # 3. Channel Match

        for channel in self.get_channels():

            candidates = [channel["name"]]
            candidates.extend(channel.get("previous_names", []))

            for value in candidates:

                value = self.normalize(value)

                if (
                    re.search(rf"\b{re.escape(entity)}\b", value)
                    or entity in value
                    or value in entity
                ):
                    return channel["id"]

        # 4. Fuzzy Match

        match = get_close_matches(
            entity,
            self.lookup.keys(),
            n=1,
            cutoff=0.75
        )

        if match:
            return self.lookup[match[0]]

        return None
    


    # Auto Text

    def slack_autotext(self, extracted_details: List[Dict]):

        """
        Input:
        [
            {
                "entity": "jainil",
                "personalized_message": "Send the requested project files."
            },
            {
                "entity": "backend team",
                "personalized_message": "Schedule a meeting."
            }
        ]
        """

        results = []

        for item in extracted_details:

            entity = item.get("entity")
            message = item.get("personalized_message")

            if not entity or not message:
                results.append({
                    "entity": entity,
                    "status": "failed",
                    "reason": "Missing entity or personalized_message"
                })
                continue

            try:

                response = self.send_message(
                    entity=entity,
                    message=message
                )

                results.append({
                    "entity": entity,
                    "status": "success",
                    "channel": response["channel"],
                    "ts": response["ts"]
                })

            except Exception as e:

                results.append({
                    "entity": entity,
                    "status": "failed",
                    "reason": str(e)
                })

        return results
    # ============================================================
    # Helpers
    # ============================================================

    def get_users(self):
        return self.workspace["users"]

    def get_channels(self):
        return self.workspace["channels"]

    def refresh(self):
        self.refresh_workspace()


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    slack = SlackService()

    # Only run this when users/channels change
    # slack.refresh()
    
    # slack.send_message(
    #     "Jainil Patel",
    #     "Hello from AI Agent 🚀"
    # )

    # slack.send_message(
    #     "general",
    #     "Deployment completed successfully ✅"
    # )

    # slack.send_message(
    #     "Finance Project",
    #     "Testing channel lookup."
    # )

    # print("\n========== USERS ==========")
    # for user in slack.get_users():
    #     print(user)

    # print("\n========== CHANNELS ==========")
    # for channel in slack.get_channels():
    #     print(channel)

    # print("\n========== LOOKUP TESTS ==========")

    # tests = [
    #     # User names
    #     "Jainil Patel",
    #     "jainil patel",
    #     "JAINIL PATEL",

    #     # Display name
    #     "jainil",

    #     # Username
    #     "jainilp",

    #     # Email
    #     "jainil@example.com",

    #     # Channels
    #     "general",
    #     "#general",
    #     "finance-project",
    #     "finance project",

    #     # Invalid
    #     "unknown person",
    #     "random channel",
    #     "mann shah",
    #     "dev"
    # ]

    # for entity in tests:
    #     print(f"{entity:<25} -> {slack.resolve_entity(entity)}")

    extracted_details = [
        {
            "entity": "jainil",
            "personalized_message": "Send the requested project files via email."
        },
        {
            "entity": "backend team",
            "personalized_message": "Schedule a meeting with the backend team."
        },
        {
            "entity": "general",
            "personalized_message": "Hello from the Slack AutoText tool 🚀"
        },
        {
            "entity": "unknown person",
            "personalized_message": "This should fail."
        }
    ]

    result = slack.slack_autotext(extracted_details)

    print("\n========== RESULTS ==========")

    print(json.dumps(result, indent=4))