from py_imessage import imessage
import time
import json
from datetime import datetime

def check_latest_imessage(phone_number):
    messages = imessage.get_chat_for_phone_number(phone_number)
    if messages:
        latest_message = messages[-1]
        return latest_message["text"], datetime.strptime(latest_message["date"], "%Y-%m-%d %H:%M:%S")
    else:
        return None, None
