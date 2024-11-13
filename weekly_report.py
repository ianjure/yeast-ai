from pymessenger import Bot
import os

# Access token for the bot (stored in GitHub secrets)
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
bot = Bot(PAGE_ACCESS_TOKEN)

# List of user IDs to send the message to
USER_IDS = ["USER_ID_1", "USER_ID_2"]  # Replace with actual Facebook user IDs

def send_weekly_message():
    message = "Hello! Here’s your weekly update from our bot."
    for user_id in USER_IDS:
        bot.send_text_message(user_id, message)

if __name__ == "__main__":
    send_weekly_message()