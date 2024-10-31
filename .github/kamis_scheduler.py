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

        print(f"Item: {item}, Time Taken: {end_time - start_time:.2f} seconds")

        if response.status_code == 200:
            try:
                data = response.json()  # JSON 응답을 처리
                if "price" in data:  # "price" 키가 있는지 확인
                    price_info = {
                        "item": item,  # 과일 이름을 저장
                        "price": data["price"],  # 가격 정보
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    print(f"Data for {item} successfully retrieved.")
                    return price_info
                else:
                    print(f"No price information found for {item}. Response: {data}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {item}: {response.text}")
        else:
            print(f"Failed to fetch data for {item}. Status code: {response.status_code}")
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
            # 파일이 존재할 경우 읽고 없을 경우 새로 생성
            if os.path.exists('docs/eco_price_list.json'):
                with open('docs/eco_price_list.json', 'r+', encoding='utf-8') as file:
                    stored_data = json.load(file)
                    for price in all_price_data:
                        if price not in stored_data:  # 중복 항목 체크
                            stored_data.append(price)
                    file.seek(0)
                    json.dump(stored_data, file, ensure_ascii=False, indent=4)
                print("KAMIS data saved to eco_price_list.json.")
            else:
                with open('docs/eco_price_list.json', 'w', encoding='utf-8') as file:
                    json.dump(all_price_data, file, ensure_ascii=False, indent=4)
                print("eco_price_list.json created and data saved.")
        except Exception as e:
            print(f"Error saving eco_price_list.json: {e}")
    else:
        print("No KAMIS data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)
        
        # JSON 파일을 스테이징
        subprocess.run(["git", "add", "docs/eco_price_list.json"], check=True)
        
        # 변경 사항이 있을 때만 커밋
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update KAMIS data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_kamis_data()
