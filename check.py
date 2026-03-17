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

# 讀產品列表
products = json.load(open("products.json"))

# 讀狀態檔
try:
    status = json.load(open("price_status.json"))
except:
    status = {}

changed = False

for p in products:
    html = requests.get(
        p["url"],
        headers={"User-Agent": "Mozilla/5.0"}
    ).text

    # 正則抓價格
    match = re.search(r'\$([0-9]+\.[0-9]+)', html)

    if not match:
        continue

    price = float(match.group(1))
    print(p["name"], price)

    notified = status.get(p["name"], False)

    # 價格低於 target 且未通知 → 發送 Telegram
    if price <= p["target"] and not notified:
        msg = f"""🔥 Price Drop!

{p['name']}

Price: ${price}
Target: ${p['target']}

{p['url']}
"""
        send(msg)
        status[p["name"]] = True
        changed = True

    # 價格回升 → 重置通知狀態
    elif price > p["target"] and notified:
        status[p["name"]] = False
        changed = True

# 儲存狀態
if changed:
    with open("price_status.json", "w") as f:
        json.dump(status, f)
