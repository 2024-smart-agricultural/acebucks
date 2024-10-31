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

def get_period_product_list():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&apikey={api_key}"

        print(f"Fetching data from URL: {url}")  # 요청 URL 로그

        headers = {
            'Content-Type': 'application/json',  # 또는 'application/xml' 필요 시 추가
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        response = requests.get(url, timeout=10)
        print("Response status code:", response.status_code)
        print("Response content:", response.content)  # 응답 내용 출력
        response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생

        if response.status_code == 200:
            # XML 응답 파싱
            root = ET.fromstring(response.content)
            items = root.findall('.//item')  # XML 구조에 따라 조정 필요
            filtered_data = filter_desired_items(items)

            return {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for period product list. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching period product list: {e}")
        return None

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        item_name = item.find('itemname').text if item.find('itemname') is not None else ''
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append({
                "itemname": item_name,
                # 필요한 다른 데이터 추가
            })
    return filtered_items

def save_period_product_list():
    new_data = get_period_product_list()
    if new_data and new_data['all_data']:
        try:
            with open('docs/period_product_list.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("period_product_list.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No period product data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/period_product_list.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update period product list data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_period_product_list()
