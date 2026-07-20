# from slack_sdk import WebClient
# import os
# from dotenv import load_dotenv
# load_dotenv()

# tok = os.getenv("PA_BOT_TOKEN")

# client = WebClient(token=tok)

# # client.chat_postMessage(
# #     channel="U0BDE4F3ZUM",  # User ID
# #     text="HEyyy"
# # )

# print(client.chat_postMessage(
#     channel="U0BDE4F3ZUM",  # User ID
#     text="HEyyy",
#     as_user=True
# ))


# import os
# from dotenv import load_dotenv
# from slack_sdk import WebClient

# load_dotenv()

# if not USER_TOKEN:
#     raise Exception("USER_TOKEN not found")

# client = WebClient(token=USER_TOKEN)

# print(client.chat_postMessage(
#     channel="U05SPJETPNE",  # User ID
#     text="HOllalaaa",
#     token=USER_TOKEN
# ))
# response = client.conversations_open(
#     users=["U0BDE4F3ZUM"]
# )

# print(response)