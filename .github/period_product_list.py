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

def fetch_period_product_list():
    try:
        print("Running Period Product List data collection...")
        
        # API 요청 URL
        url = 'http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&apikey=***'
        print(f"Fetching data from URL: {url}")
        
        # API 요청
        response = requests.get(url)
        
        # 응답 상태 확인
        if response.status_code == 200:
            print("Response status code:", response.status_code)
            print("Response content:", response.text)  # XML 응답 내용 확인
            
            # XML 데이터 파싱
            root = ET.fromstring(response.text)
            
            # XML에서 필요한 데이터 추출
            period_product_data = []
            for item in root.findall(".//item"):
                item_name = item.find('itemname').text if item.find('itemname') is not None else ''
                if any(keyword in item_name for keyword in desired_keywords):
                    period_product_data.append({
                        "itemname": item_name,
                        # 필요한 다른 데이터 추가
                    })
            
            if period_product_data:
                print("Period product data collected:", period_product_data)
                return period_product_data
            else:
                print("No period product data found matching keywords.")
                return []
        else:
            print(f"Failed to fetch period product list. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        print("Error occurred while fetching period product list:", e)
        print("No period product data collected.")
        return []

# 호출 예제
fetch_period_product_list()

def save_period_product_list():
    new_data = fetch_period_product_list()
    if new_data:
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
