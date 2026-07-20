import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)


# ============================================================
# USERS
# ============================================================

def get_user(user_id: str):
    """Get information about a user."""

    try:
        response = client.users_info(user=user_id)
        return response["user"]

    except SlackApiError as e:
        print(e.response["error"])
        return None


def get_users():
    """Return all workspace users."""

    users = []
    cursor = None

    while True:

        response = client.users_list(cursor=cursor)

        users.extend(response["members"])

        cursor = (
            response.get("response_metadata", {})
            .get("next_cursor")
        )

        if not cursor:
            break

    return users


def find_user_by_name(name: str):
    """Find user using real name or username."""

    name = name.lower()

    for user in get_users():

        real_name = user.get("real_name", "").lower()
        username = user.get("name", "").lower()
        display_name = (
            user.get("profile", {})
            .get("display_name", "")
            .lower()
        )

        if (
            name == real_name
            or name == username
            or name == display_name
        ):
            return user

    return None


# ============================================================
# CHANNELS
# ============================================================

def get_channel(channel_id: str):
    """Get channel details."""

    try:

        response = client.conversations_info(
            channel=channel_id
        )

        return response["channel"]

    except SlackApiError as e:

        print(e.response["error"])
        return None


def get_channels():
    """Return all public and private channels."""

    channels = []
    cursor = None

    while True:

        response = client.conversations_list(
            types="public_channel,private_channel",
            cursor=cursor,
        )

        channels.extend(response["channels"])

        cursor = (
            response.get("response_metadata", {})
            .get("next_cursor")
        )

        if not cursor:
            break

    return channels


def find_channel(name: str):
    """Find channel by name."""

    name = name.lower()

    for channel in get_channels():

        if channel["name"].lower() == name:
            return channel

    return None


def join_channel(channel_id: str):
    """Join a public channel."""

    try:

        client.conversations_join(channel=channel_id)

        return True

    except SlackApiError as e:

        print(e.response["error"])
        return False


# MESSAGING

def send_message(
    channel_id: str,
    message: str,
    thread_ts: str = None,
):
    """
    Send message to a channel, group or DM.
    """

    try:

        response = client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=thread_ts,
        )

        return response

    except SlackApiError as e:

        print(e.response["error"])
        return None


def send_dm(
    user_id: str,
    message: str,
):
    """
    Send DM to a user.
    """

    try:

        conversation = client.conversations_open(
            users=user_id
        )

        channel_id = conversation["channel"]["id"]

        return send_message(
            channel_id,
            message,
        )

    except SlackApiError as e:

        print(e.response["error"])
        return None


def reply_thread(
    channel_id: str,
    thread_ts: str,
    message: str,
):
    """
    Reply inside a thread.
    """

    return send_message(
        channel_id,
        message,
        thread_ts=thread_ts,
    )


def update_message(
    channel_id: str,
    ts: str,
    message: str,
):
    """Update an existing message."""

    try:

        return client.chat_update(
            channel=channel_id,
            ts=ts,
            text=message,
        )

    except SlackApiError as e:

        print(e.response["error"])
        return None


def delete_message(
    channel_id: str,
    ts: str,
):
    """Delete a message."""

    try:

        return client.chat_delete(
            channel=channel_id,
            ts=ts,
        )

    except SlackApiError as e:

        print(e.response["error"])
        return None


# ============================================================
# HISTORY
# ============================================================

def get_messages(
    channel_id: str,
    limit: int = 20,
):
    """Fetch recent messages."""

    try:

        response = client.conversations_history(
            channel=channel_id,
            limit=limit,
        )

        return response["messages"]

    except SlackApiError as e:

        print(e.response["error"])
        return []


# ============================================================
# FILES
# ============================================================

def upload_file(
    channel_id: str,
    file_path: str,
    title: str = None,
):
    """Upload a file."""

    try:

        return client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            title=title,
        )

    except SlackApiError as e:

        print(e.response["error"])
        return None


# ============================================================
# REACTIONS
# ============================================================

def add_reaction(
    channel_id: str,
    timestamp: str,
    emoji: str,
):
    """Add emoji reaction."""

    try:

        return client.reactions_add(
            channel=channel_id,
            timestamp=timestamp,
            name=emoji,
        )

    except SlackApiError as e:

        print(e.response["error"])
        return None


# ============================================================
# LOOKUPS
# ============================================================

def get_channel_members(channel_id: str):
    """Return members of a channel."""

    try:

        response = client.conversations_members(
            channel=channel_id
        )

        return response["members"]

    except SlackApiError as e:

        print(e.response["error"])
        return []


def get_user_presence(user_id: str):
    """Get online/away status."""

    try:

        response = client.users_getPresence(
            user=user_id
        )

        return response["presence"]

    except SlackApiError as e:

        print(e.response["error"])
        return None


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    print("Users")
    print(get_users())


    print("Channels")
    print(get_channels())

    # Example
    #
    # send_dm(
    #     "U12345678",
    #     "Hello from Python!"
    # )
    #
    # channel = find_channel("general")
    #
    # if channel:
    #     send_message(
    #         channel["id"],
    #         "Hello everyone!"
    #     )