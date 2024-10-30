import subprocess
import os
import json
import requests
from datetime import datetime

def get_period_product_data(item_code):
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&apikey={api_key}&p_itemcode={item_code}&p_returntype=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            product_info = {
                "item_code": item_code,
                "data": data.get("data", []),  # 모든 데이터 가져오기
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return product_info
        else:
            print(f"Failed to fetch data for item_code {item_code}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching period product data for item_code {item_code}: {e}")
        return None

def save_period_product_data():
    item_codes = ["tomato", "melon", "banana", "pineapple", "lemon"]
    all_product_data = []

    for item_code in item_codes:
        new_data = get_period_product_data(item_code)
        if new_data:
            all_product_data.append(new_data)

    # JSON 파일에 데이터를 저장
    if all_product_data:
        with open('docs/period_product_list.json', 'w') as file:
            json.dump(all_product_data, file, ensure_ascii=False, indent=4)
        print("period_product_list.json created and data saved.")
    else:
        print("No period product data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "you@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Your Name"])
    
    # JSON 파일을 스테이징
    subprocess.run(["git", "add", "docs/eco_price_list.json", "docs/period_product_list.json"])
    
    # 변경 사항이 있을 때만 커밋
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update KAMIS data"])
        subprocess.run(["git", "push"])
    else:
        print("No changes to commit.")

save_period_product_data()
