import requests
from bs4 import BeautifulSoup
import json
import os
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 讀產品
products = json.load(open("products.json"))

# 讀狀態
try:
    status = json.load(open("price_status.json"))
except:
    status = {}

changed = False

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-AU,en;q=0.9",
    "Referer": "https://www.chemistwarehouse.com.au/"
}

def get_price(url):
    for attempt in range(3):  # retry 3 次
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            # ✅ 方法1：抓 h2 主價格
            tag = soup.find("h2", class_="display-l text-colour-title-light")
            if tag:
                return float(tag.text.strip().replace("$", ""))

            # 🔁 fallback：抓 span Price
            tag = soup.find("span", class_="Price")
            if tag:
                return float(tag.text.strip().replace("$", ""))

        except Exception as e:
            print("Error:", e)

        time.sleep(5)  # 等 5 秒再試

    return None


for p in products:
    price = get_price(p["url"])

    if price is None:
        print(f"❌ 抓不到價格: {p['name']}")
        send(f"⚠️ 抓不到價格: {p['name']}")
        continue

    print(f"{p['name']} 價格: {price}")

    notified = status.get(p["name"], False)

    # 🔥 價格低於 target
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

    # 🔄 價格回升
    elif price > p["target"] and notified:
        status[p["name"]] = False
        changed = True


if changed:
    with open("price_status.json", "w") as f:
        json.dump(status, f)
