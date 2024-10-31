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

def get_regional_item_prices():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/json.do?action=ItemInfo&apikey={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # 응답 내용을 출력하여 확인
        print(response.text)  # API 응답 내용을 출력

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                filtered_data = filter_desired_items(data['data'])
                return {
                    "all_data": filtered_data,
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                print("No data found in response.")
                return None
        else:
            print(f"Failed to fetch data for regional item prices. Status code: {response.status_code}")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        print(f"Error occurred while fetching regional item prices: {e}")
        return None

def filter_desired_items(items):
    filtered_items = [
        item for item in items
        if any(keyword in item.get('itemname', '') for keyword in desired_keywords)
    ]
    return filtered_items

def save_regional_item_prices():
    new_data = get_regional_item_prices()
    if new_data and new_data['all_data']:
        try:
            with open('docs/regional_item_prices.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("regional_item_prices.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No regional item prices data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/regional_item_prices.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update regional item prices data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_regional_item_prices()
