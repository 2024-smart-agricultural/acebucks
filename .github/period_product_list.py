
import os
import json
import requests
from datetime import datetime
import subprocess

def get_period_product_data(item_code):
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&apikey={api_key}&p_itemcode={item_code}&p_returntype=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            price_info = {
                "item_code": item_code,
                "prices": data["data"],
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return price_info
        else:
            print(f"Failed to fetch data for item_code {item_code}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching period product data for item_code {item_code}: {e}")
        return None

def save_period_product_data():
    item_codes = ["tomato", "melon", "banana", "pineapple", "lemon"]
    all_price_data = []

    for item_code in item_codes:
        new_price_data = get_period_product_data(item_code)
        if new_price_data:
            all_price_data.append(new_price_data)

    if all_price_data:
        with open('docs/period_product_list.json', 'w') as file:
            json.dump(all_price_data, file, ensure_ascii=False, indent=4)
        print("period_product_list.json created and data saved.")
    else:
        print("No period product data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "docs/period_product_list.json"])
    subprocess.run(["git", "commit", "-m", "Update period product data"])
    subprocess.run(["git", "push"])

save_period_product_data()
