import os
import json
import requests
from datetime import datetime
import subprocess
import time

def get_kamis_data(item):
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&key={api_key}&categoryCode=200&itemCode={item}&productClsCode=01&startDay=20240101&endDay=20241231&countryCode=1101&type=json"

        start_time = time.time()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        end_time = time.time()

        print(f"Item: {item}, Time Taken: {end_time - start_time} seconds")

        if response.status_code == 200:
            data = response.json()
            price_info = {
                "item": item,  # 과일 이름을 저장
                "price": data.get("price"),  # 가격 정보가 "price"에 있다고 가정
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"Data for {item} successfully retrieved.")
            return price_info
        else:
            print(f"Failed to fetch data for {item}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching KAMIS data for {item}: {e}")
        return None

def save_kamis_data():
    item_list = ["tomato", "melon", "banana", "pineapple", "lemon"]
    all_price_data = []

    for item in item_list:
        new_price = get_kamis_data(item)
        if new_price:
            all_price_data.append(new_price)

    if all_price_data:
        try:
            with open('docs/eco_price_list.json', 'r+', encoding='utf-8') as file:
                stored_data = json.load(file)
                for price in all_price_data:
                    # 중복 항목이 없는 경우만 추가
                    if price not in stored_data:
                        stored_data.append(price)
                file.seek(0)
                json.dump(stored_data, file, ensure_ascii=False, indent=4)
            print("KAMIS data saved to eco_price_list.json.")
        except FileNotFoundError:
            with open('docs/eco_price_list.json', 'w', encoding='utf-8') as file:
                json.dump(all_price_data, file, ensure_ascii=False, indent=4)
            print("eco_price_list.json created and data saved.")
    else:
        print("No KAMIS data collected.")

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

save_kamis_data()
