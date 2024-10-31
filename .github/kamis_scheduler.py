import os
import json
import requests
from datetime import datetime
import subprocess

# 원하는 키워드 리스트
desired_keywords = [
    '고구마', '수박', '토마토', '딸기', '당근', '멜론', '사과',
    '배', '복숭아', '포도', '감귤', '단감', '바나나', '파인애플',
    '오렌지', '자몽', '레몬', '체리', '망고', '블루베리'
]

def get_eco_price_list():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/json.do?action=EcoPriceList&apikey={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # 응답 내용을 출력
        print(response.text)  # 여기에서 API 응답 내용을 출력

        if response.status_code == 200:
            data = response.json()
            filtered_data = filter_desired_items(data.get('data', []))
            return {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for eco price list. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching eco price list: {e}")
        return None

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        item_name = item.get('itemname', '')
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append(item)
    return filtered_items

def save_eco_price_list():
    new_data = get_eco_price_list()
    if new_data and new_data['all_data']:
        try:
            with open('docs/eco_price_list.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("eco_price_list.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No KAMIS data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/eco_price_list.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update eco price list data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_eco_price_list()
