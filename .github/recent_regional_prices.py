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

def fetch_daily_prices_by_category():
    try:
        print("Running Daily Prices by Category data collection...")
        
        # API 요청 URL 및 파라미터 설정
        url = 'http://www.kamis.or.kr/service/price/xml.do?action=dailyPricesByCategoryList'
        params = {
            'p_product_cls_code': '02',  # 농산물 코드
            'p_category_code': '100',    # 카테고리 코드 설정
            'p_regday': '2024-10-31',    # 날짜 설정
            'p_convert_kg_yn': 'N',      # kg 변환 여부
            'p_cert_key': 'YOUR_API_KEY',  # API 인증 키 입력
            'p_cert_id': 'YOUR_CERT_ID',   # 인증 ID 입력
            'p_returntype': 'json'         # JSON으로 응답 요청
        }
        
        # API 요청
        response = requests.get(url, params=params)
        
        # 응답 상태 코드 및 내용 출력
        print("Response status code:", response.status_code)
        print("Response content:", response.content)
        
        # 응답 상태 확인
        if response.status_code == 200:
            # JSON 데이터 파싱
            data = response.json()
            
            if "data" in data and data["data"]:
                for item in data["data"]:
                    print(f"Price: {item}")
                return data["data"]
            else:
                print("No daily prices data found in response.")
                return []
        else:
            print(f"Failed to fetch daily prices by category. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        print("Error occurred while fetching daily prices by category:", e)
        return []

# 호출 예제
fetch_daily_prices_by_category()

def filter_desired_items(items):
    # 필터링된 아이템 리스트 초기화
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
    # 가격 데이터를 가져오는 함수 호출
    new_data = fetch_daily_prices_by_category()
    
    if new_data:
        try:
            # JSON 파일에 데이터 저장
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
        # Git 사용자 정보 설정
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        # JSON 파일 추가
        subprocess.run(["git", "add", "docs/regional_item_prices.json"], check=True)

        # 변경사항 커밋 및 푸시
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update regional item prices data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

# 메인 실행
if __name__ == "__main__":
    save_regional_item_prices()
