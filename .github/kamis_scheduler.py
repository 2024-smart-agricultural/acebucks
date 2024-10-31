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

def fetch_eco_price_list():
    try:
        print("Running EcoPriceList data collection...")

        # 올바른 API 요청 URL 사용
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=EcoPriceList&apikey={api_key}"
        
        response = requests.get(url)
        
        # 응답 상태 확인
        if response.status_code == 200:
            print("Response content:", response.content)
            data = response.json()

            # JSON 데이터 처리
            if data.get("data"):
                eco_price_data = data["data"]
                print("Eco price data collected:", eco_price_data)
                return eco_price_data
            else:
                print("No eco price data found in response.")
                return []
        else:
            print(f"Failed to fetch eco price list. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        print("Error occurred while fetching eco price list:", e)
        print("No eco price data collected.")
        return []

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        item_name = item  # JSON 응답에서 item의 이름을 추출하는 방법에 따라 수정
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append({
                "itemname": item_name,
                # 필요한 다른 데이터 추가
            })
    return filtered_items

def save_eco_price_list():
    # fetch_eco_price_list()로 데이터를 가져옵니다
    raw_data = fetch_eco_price_list()
    
    # 필터링된 데이터를 사용하여 저장합니다
    filtered_data = filter_desired_items(raw_data)
    if filtered_data:
        try:
            os.makedirs('docs', exist_ok=True)
            with open('docs/eco_price_list.json', 'w', encoding='utf-8') as file:
                json.dump({"all_data": filtered_data}, file, ensure_ascii=False, indent=4)
            print("eco_price_list.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No eco price data collected.")

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
