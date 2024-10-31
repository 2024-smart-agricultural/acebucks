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

def get_daily_prices_by_category():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&apikey={api_key}&p_returntype=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            filtered_data = filter_data_by_keywords(data)
            category_info = {
                "all_data": filtered_data,  # 필터링된 데이터 저장
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return category_info
        else:
            print(f"Failed to fetch data for daily prices by category. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching daily prices by category: {e}")
        return None

def filter_data_by_keywords(data):
    # 특정 키워드가 포함된 데이터 필터링
    filtered_items = [
        item for item in data['data']['item']
        if any(keyword in item['productName'] for keyword in desired_keywords)
    ]
    data['data']['item'] = filtered_items
    return data

def save_daily_prices_by_category():
    new_data = get_daily_prices_by_category()
    if new_data:
        with open('docs/daily_prices_by_category.json', 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
        print("daily_prices_by_category.json created and data saved.")
    else:
        print("No daily prices by category data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "you@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Your Name"])

    # JSON 파일을 스테이징
    subprocess.run(["git", "add", "docs/daily_prices_by_category.json"])

    # 변경 사항이 있을 때만 커밋
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update daily prices by category data"])
        subprocess.run(["git", "push"])
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    save_daily_prices_by_category()
