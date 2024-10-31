import os
import json
import requests
import subprocess

# 원하는 키워드 리스트
desired_keywords = [
    '고구마', '수박', '토마토', '딸기', '당근', '멜론', '사과',
    '배', '복숭아', '포도', '감귤', '단감', '바나나', '파인애플',
    '오렌지', '자몽', '레몬', '체리', '망고', '블루베리'
]

def fetch_daily_county_list():
    print("Running Daily County Prices data collection...")
    
    # API 요청 URL 및 파라미터 설정
    url = 'http://www.kamis.or.kr/service/price/xml.do?action=dailyCountyList'
    params = {
        'p_product_cls_code': '02',  # 농산물 코드
        'p_category_code': '100',    # 카테고리 코드 설정
        'p_regday': today,    # 날짜 설정
        'p_convert_kg_yn': 'N',      # kg 변환 여부
        'p_cert_key': os.getenv('KAMIS_KEY'),  # API 인증 키
        'p_cert_id': os.getenv('P_CERT_ID')     # 인증 ID
        'p_returntype': 'json'         # JSON으로 응답 요청
    }
    
    try:
        response = requests.get(url, params=params)
        
        # 응답 상태 코드 및 내용 출력
        print("Response status code:", response.status_code)
        print("Response content:", response.content.decode())  # 바이트 문자열을 디코드하여 출력
        
        # 응답 상태 확인
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                return data["data"]
            else:
                print("No daily county prices data found in response.")
        else:
            print(f"Failed to fetch daily county prices. Status code: {response.status_code}")
    
    except Exception as e:
        print("Error occurred while fetching daily county prices:", e)
    
    return []

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        item_name = item.get('itemname', '')
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append({
                "itemname": item_name,
                # 필요한 다른 데이터 추가 가능
            })
    return filtered_items

def save_regional_item_prices():
    new_data = fetch_daily_county_list()
    
    if new_data:
        try:
            os.makedirs('docs', exist_ok=True)
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
