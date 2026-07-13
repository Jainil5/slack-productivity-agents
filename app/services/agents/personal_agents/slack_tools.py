# Optimized slack_tools.py
import json
import logging
import os
import re
from difflib import get_close_matches
from typing import Dict, List

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackService:
    CACHE_FILE = "app/data/slack_workspace.json"

    def __init__(self):
        load_dotenv()

        self.bot_token = os.getenv("PA_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN not found in .env")

        self.client = WebClient(token=self.bot_token)

        self.workspace = {"users": [], "channels": []}
        self.lookup: Dict[str, str] = {}
        self.search_index: List[Dict] = []

        self.load_cache()

    @staticmethod
    def normalize(text: str) -> str:
        return re.sub(r"[\W_]+", " ", str(text).lower()).strip()

    def refresh_workspace(self):
        users, channels = [], []

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

        cursor = None
        while True:
            response = self.client.conversations_list(
                types="public_channel,private_channel",
                limit=1000,
                cursor=cursor,
            )

            for channel in response["channels"]:
                channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "previous_names": channel.get("previous_names", []),
                })

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        self.workspace = {"users": users, "channels": channels}
        self.build_lookup()
        self.save_cache()
        logger.info("Workspace refreshed.")

    def save_cache(self):
        os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
        with open(self.CACHE_FILE, "w") as f:
            json.dump(self.workspace, f, indent=4)

    def load_cache(self):
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, "r") as f:
                self.workspace = json.load(f)
            self.build_lookup()
        else:
            self.refresh_workspace()

    def build_lookup(self):
        self.lookup.clear()
        self.search_index.clear()

        def add(value: str, slack_id: str):
            if not value:
                return
            value = self.normalize(value)
            self.lookup[value] = slack_id
            self.search_index.append({"text": value, "id": slack_id})

        for user in self.workspace["users"]:
            for value in (
                user["real_name"],
                user["display_name"],
                user["username"],
                user["email"],
            ):
                add(value, user["id"])

        for channel in self.workspace["channels"]:
            add(channel["name"], channel["id"])
            for old in channel.get("previous_names", []):
                add(old, channel["id"])

    def resolve_entity(self, entity: str):
        entity = self.normalize(entity)

        if entity in self.lookup:
            return self.lookup[entity]

        for item in self.search_index:
            text = item["text"]
            if entity in text or text in entity or re.search(rf"\b{re.escape(entity)}\b", text):
                return item["id"]

        match = get_close_matches(entity, self.lookup.keys(), n=1, cutoff=0.75)
        return self.lookup[match[0]] if match else None

    def send_message(self, entity: str, message: str):
        """
        Send a Slack message.

        Supports:
        - User name/email/display name -> DM
        - User ID (U...)              -> DM
        - Channel name                -> Channel
        - Channel ID (C...)           -> Channel
        - DM Channel ID (D...)        -> Existing DM
        """

        slack_id = (
            entity
            if entity.startswith(("U", "C", "D"))
            else self.resolve_entity(entity)
        )

        if not slack_id:
            raise ValueError(f"'{entity}' not found in Slack workspace.")

        destination = ""
        final_channel = ""

        # ---------------- DM to User ----------------
        if slack_id.startswith("U"):
            dm = self.client.conversations_open(users=[slack_id])
            final_channel = dm["channel"]["id"]

            self.client.chat_postMessage(
                channel=final_channel,
                text=message,
            )

            user = next(
                (u for u in self.workspace["users"] if u["id"] == slack_id),
                None,
            )

            name = (
                user.get("real_name")
                or user.get("display_name")
                or user.get("username")
                if user
                else slack_id
            )

            destination = f"DM -> {name}"

        # ---------------- Existing DM ----------------
        elif slack_id.startswith("D"):
            final_channel = slack_id

            self.client.chat_postMessage(
                channel=final_channel,
                text=message,
            )

            destination = f"Existing DM ({slack_id})"

        # ---------------- Channel ----------------
        else:
            final_channel = slack_id

            self.client.chat_postMessage(
                channel=final_channel,
                text=message,
            )

            channel = next(
                (c for c in self.workspace["channels"] if c["id"] == slack_id),
                None,
            )

            channel_name = channel["name"] if channel else slack_id
            destination = f"Channel -> #{channel_name}"

        print("=" * 70)
        print("✅ Slack message sent successfully")
        print(f"📍 Destination : {destination}")
        print(f"🆔 Channel ID  : {final_channel}")
        print(f"💬 Message     : {message}")
        print("=" * 70)

        return {
            "destination": destination,
            "channel": final_channel,
            "message": message,
        }
    def slack_autotext(self, extracted_details: List[Dict]):
        results = []

        for item in extracted_details:
            entity = item.get("entity")
            message = item.get("personalized_message")

            if not entity or not message:
                results.append({
                    "entity": entity,
                    "status": "failed",
                    "reason": "Missing entity or personalized_message",
                })
                continue

            try:
                slack_id = self.resolve_entity(entity)

                if not slack_id:
                    raise ValueError(f"'{entity}' not found.")

                response = self.send_message(slack_id, message)
                print("RESSS:",response)
                results.append({
                    "entity": entity,
                    "resolved_id": slack_id,
                    "status": "success",
                    "channel": response["channel"],
                    "timestamp": response["ts"],
                })

            except Exception as e:
                results.append({
                    "entity": entity,
                    "status": "failed",
                    "reason": str(e),
                })

        return results

    def get_users(self):
        return self.workspace["users"]

    def get_channels(self):
        return self.workspace["channels"]

    def refresh(self):
        self.refresh_workspace()
