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

# 模擬完整瀏覽器 User-Agent
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

for p in products:
    try:
        html = requests.get(p["url"], headers=headers, timeout=10).text
    except Exception as e:
        send(f"⚠️ 無法抓取 {p['name']} 網頁: {e}")
        continue

    # 正則抓價格
    match = re.search(r'\$([0-9]+\.[0-9]+)', html)

    if not match:
        # 抓不到價格，打印前 500 字方便 debug
        print(f"⚠️ 無法抓到 {p['name']} 的價格，HTML 前500字:")
        print(html[:500])
        send(f"⚠️ {p['name']} 抓不到價格，請檢查防爬蟲或網頁變更")
        continue

    price = float(match.group(1))
    print(f"{p['name']} 目前價格: {price}")

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
