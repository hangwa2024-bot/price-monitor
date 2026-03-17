import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import re
import requests

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

# Selenium 設定
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for p in products:
    try:
        driver.get(p["url"])
        time.sleep(3)  # 等 JS 渲染
        html = driver.page_source
    except Exception as e:
        send(f"⚠️ 無法抓取 {p['name']} 網頁: {e}")
        continue

    # 抓價格
    match = re.search(r'\$([0-9]+\.[0-9]+)', html)
    if not match:
        print(f"⚠️ 無法抓到 {p['name']} 的價格，HTML 前500字:")
        print(html[:500])
        send(f"⚠️ {p['name']} 抓不到價格，請檢查防爬蟲或網頁變更")
        continue

    price = float(match.group(1))
    print(f"{p['name']} 目前價格: {price}")

    notified = status.get(p["name"], False)

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
    elif price > p["target"] and notified:
        status[p["name"]] = False
        changed = True

if changed:
    with open("price_status.json", "w") as f:
        json.dump(status, f)

driver.quit()
