import requests
import json
import re
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

products = json.load(open("products.json"))

for p in products:

    html = requests.get(
        p["url"],
        headers={"User-Agent": "Mozilla/5.0"}
    ).text

    match = re.search(r'\$([0-9]+\.[0-9]+)', html)

    if not match:
        continue

    price = float(match.group(1))

    print(p["name"], price)

    if price <= p["target"]:

        msg = f"""🔥 Price Drop!

{p['name']}

Price: ${price}
Target: ${p['target']}

{p['url']}
"""

        send(msg)
