import csv

from app.services.myslack.slack_tools import (
    get_users,
    get_channels,
)

DATABASE_FILE = "app/data/slack_dir.csv"


# CSV COLUMNS

FIELDS = [

    "entity_id",
    "entity_type",

    "slack_id",
    "team_id",

    "name",
    "display_name",
    "username",

    "first_name",
    "last_name",

    "email",

    "is_bot",
    "is_admin",
    "is_owner",

    "channel_members",

    "is_general",
    "is_private",
    "is_archived",

    "previous_names",

    "purpose",
    "topic",

]


# BUILD DATABASE

def refresh_database():
    """
    Download all Slack users and channels
    and rebuild the local CSV.
    """

    users = get_users()
    channels = get_channels()

    with open(
        DATABASE_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        writer.writeheader()

        # ----------------------------------------
        # USERS
        # ----------------------------------------

        for user in users:

            profile = user.get(
                "profile",
                {}
            )

            writer.writerow(

                {

                    "entity_id": user["id"],
                    "entity_type": "USER",

                    "slack_id": user["id"],
                    "team_id": user.get(
                        "team_id"
                    ),

                    "name": profile.get(
                        "real_name"
                    ),

                    "display_name": profile.get(
                        "display_name"
                    ),

                    "username": user.get(
                        "name"
                    ),

                    "first_name": profile.get(
                        "first_name"
                    ),

                    "last_name": profile.get(
                        "last_name"
                    ),

                    "email": profile.get(
                        "email"
                    ),

                    "is_bot": user.get(
                        "is_bot"
                    ),

                    "is_admin": user.get(
                        "is_admin"
                    ),

                    "is_owner": user.get(
                        "is_owner"
                    ),

                    "channel_members": "",

                    "is_general": "",

                    "is_private": "",

                    "is_archived": "",

                    "previous_names": "",

                    "purpose": "",

                    "topic": "",

                }

            )

        # ----------------------------------------
        # CHANNELS
        # ----------------------------------------

        for channel in channels:

            writer.writerow(

                {

                    "entity_id": channel["id"],

                    "entity_type": "CHANNEL",

                    "slack_id": channel["id"],

                    "team_id": channel.get(
                        "context_team_id"
                    ),

                    "name": channel.get(
                        "name"
                    ),

                    "display_name": "",

                    "username": "",

                    "first_name": "",

                    "last_name": "",

                    "email": "",

                    "is_bot": "",

                    "is_admin": "",

                    "is_owner": "",

                    "channel_members": channel.get(
                        "num_members"
                    ),

                    "is_general": channel.get(
                        "is_general"
                    ),

                    "is_private": channel.get(
                        "is_private"
                    ),

                    "is_archived": channel.get(
                        "is_archived"
                    ),

                    "previous_names": ",".join(
                        channel.get(
                            "previous_names",
                            []
                        )
                    ),

                    "purpose": channel.get(
                        "purpose",
                        {}
                    ).get(
                        "value"
                    ),

                    "topic": channel.get(
                        "topic",
                        {}
                    ).get(
                        "value"
                    ),

                }

            )


# ============================================================
# LOAD DATABASE
# ============================================================

def load_database():
    """
    Return every row from the directory.
    """

    if not DATABASE_FILE.exists():
        refresh_database()

    rows = []

    with open(
        DATABASE_FILE,
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        rows.extend(reader)

    return rows


# ============================================================
# GET ENTITY
# ============================================================

def get_entity(
    slack_id: str,
):
    """
    Lookup by Slack ID.
    """

    for row in load_database():

        if row["slack_id"] == slack_id:
            return row

    return None


# ============================================================
# GET USERS
# ============================================================

def get_user_directory():

    return [

        row

        for row in load_database()

        if row["entity_type"] == "USER"

    ]


# ============================================================
# GET CHANNELS
# ============================================================

def get_channel_directory():

    return [

        row

        for row in load_database()

        if row["entity_type"] == "CHANNEL"

    ]


# ============================================================
# REBUILD
# ============================================================

if __name__ == "__main__":

    refresh_database()

    print(
        f"Database created at {DATABASE_FILE}"
    )

    print(
        f"Total records: {len(load_database())}"
    )