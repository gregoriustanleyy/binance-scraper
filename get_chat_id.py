import requests

def get_updates(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    return response.json()

bot_token = "6119013820:AAEqWzgHH4qnideh3hs9Mug3iGEzSYKZZ3k"  # Replace with your bot token

updates = get_updates(bot_token)

# Check if there are any updates
if updates["result"]:
    # Get the chat id of the last received message
    chat_id = updates["result"][-1]["message"]["chat"]["id"]
    print(f"The chat_id is: {chat_id}")
else:
    print("No messages received yet.")
