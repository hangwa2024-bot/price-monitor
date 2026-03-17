import requests
import json
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# 讀產品
products = json.load(open("products.json"))

# 發送測試訊息
for p in products:
    msg = f"""🧪 TEST MESSAGE

Product: {p['name']}
URL: {p['url']}
Target: {p['target']}

This is a test to confirm your Telegram bot works.
"""
    send(msg)
    print(f"Sent test message for {p['name']}")
