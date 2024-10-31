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
        
        # API 요청
        response = requests.get('https://api.example.com/eco_price_list')
        
        # 응답 상태 확인
        if response.status_code == 200:
            print("Response content:", response.content)
            data = response.json()
            
            # JSON 데이터 처리
            if data.get("data"):
                eco_price_data = data["data"]
                print("Eco price data collected:", eco_price_data)
            else:
                print("No eco price data found in response.")
        else:
            print(f"Failed to fetch eco price list. Status code: {response.status_code}")
    
    except Exception as e:
        print("Error occurred while fetching eco price list:", e)
        print("No eco price data collected.")

fetch_eco_price_list()

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        # item의 구조에 따라 아래 코드를 수정하세요
        item_name = item  # JSON 응답에서 item의 이름을 추출하는 방법에 따라 수정
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append({
                "itemname": item_name,
                # 필요한 다른 데이터 추가
            })
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
