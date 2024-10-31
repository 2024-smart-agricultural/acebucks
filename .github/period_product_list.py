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

def get_all_item_codes():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=ItemCodeList&apikey={api_key}&p_returntype=json"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            # API에서 모든 item_code 추출
            item_codes = [item['item_code'] for item in data['data']['item']]
            return item_codes
        else:
            print(f"Failed to fetch item codes. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred while fetching item codes: {e}")
        return []

def get_period_product_data(item_code):
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&apikey={api_key}&p_itemcode={item_code}&p_returntype=json"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            # 전체 데이터를 저장하고 날짜 형식을 년-월-일로 설정
            product_info = {
                "item_code": item_code,
                "all_data": data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return product_info
        else:
            print(f"Failed to fetch data for item_code {item_code}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching period product data for item_code {item_code}: {e}")
        return None

def save_period_product_data():
    item_codes = get_all_item_codes()  # 모든 품목 코드를 불러옴
    all_product_data = []

    for item_code in item_codes:
        new_data = get_period_product_data(item_code)
        if new_data and is_desired_product(new_data):
            all_product_data.append(new_data)
            print(f"Collected data for: {item_code}")

    if all_product_data:
        # 모든 정보를 포함한 JSON 파일을 생성하고 UTF-8 인코딩 사용
        with open('docs/period_product_list.json', 'w', encoding='utf-8') as file:
            json.dump(all_product_data, file, ensure_ascii=False, indent=4)
        print("period_product_list.json created and data saved.")
    else:
        print("No period product data collected.")

    commit_and_push_changes()

def is_desired_product(product_info):
    # product_info에서 원하는 키워드가 포함되어 있는지 체크
    if 'data' in product_info['all_data']:
        for item in product_info['all_data']['data']:
            product_name = item.get('productName', '')
            if any(keyword in product_name for keyword in desired_keywords):
                return True
    return False

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "you@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Your Name"])
    
    # JSON 파일을 스테이징
    subprocess.run(["git", "add", "docs/period_product_list.json"])
    
    # 변경 사항이 있을 때만 커밋
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update KAMIS data"])
        subprocess.run(["git", "push"])
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    save_period_product_data()
