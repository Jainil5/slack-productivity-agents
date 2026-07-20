import os

LOGIN_URL = (

    "https://slack.com/oauth/v2/authorize"

    f"?client_id={os.getenv('CLIENT_ID')}"

    "&user_scope=chat:write,im:write"

    f"&redirect_uri={os.getenv('SLACK_REDIRECT_URL')}"

)

print(LOGIN_URL)