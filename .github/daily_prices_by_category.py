import os
import json
import requests
from datetime import datetime
import subprocess
import xml.etree.ElementTree as ET

# 원하는 키워드 리스트
desired_keywords = [
    '고구마', '수박', '토마토', '딸기', '당근', '멜론', '사과',
    '배', '복숭아', '포도', '감귤', '단감', '바나나', '파인애플',
    '오렌지', '자몽', '레몬', '체리', '망고', '블루베리'
]

def get_daily_prices_by_category():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&apikey={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            # 응답 내용 출력
            print("Response content:", response.content.decode('utf-8'))

            # XML 응답 파싱
            root = ET.fromstring(response.content)
            items = root.findall('.//item')  # XML 구조에 따라 조정 필요
            filtered_data = filter_data_by_keywords(items)

            return {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for daily prices by category. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching daily prices by category: {e}")
        return None

def filter_data_by_keywords(items):
    filtered_items = []
    for item in items:
        item_name = item.find('itemname').text if item.find('itemname') is not None else ''
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append({
                "itemname": item_name,
                # 필요한 다른 데이터 추가
            })
    return filtered_items

def save_daily_prices_by_category():
    new_data = get_daily_prices_by_category()
    if new_data and new_data['all_data']:
        try:
            with open('docs/daily_prices_by_category.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("daily_prices_by_category.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No daily prices by category data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/daily_prices_by_category.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update daily prices by category data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_daily_prices_by_category()
