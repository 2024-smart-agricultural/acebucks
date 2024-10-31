import os
import json
import requests
import subprocess
import secrets  # 비밀 정보를 관리하는 모듈

# 원하는 키워드 리스트
desired_keywords = [
    '고구마', '수박', '토마토', '딸기', '당근', '멜론', '사과',
    '배', '복숭아', '포도', '감귤', '단감', '바나나', '파인애플',
    '오렌지', '자몽', '레몬', '체리', '망고', '블루베리'
]

def fetch_item_info(item_code):
    print("Running Item Info data collection...")
    
    url = 'http://www.kamis.or.kr/service/price/xml.do?action=ItemInfo'
    params = {
        'p_item_code': item_code,  # 아이템 코드
        'p_returntype': 'json',     # JSON으로 응답 요청
        'p_cert_key': os.getenv('KAMIS_KEY'),  # API 인증 키
        'p_cert_id': os.getenv('P_CERT_ID')     # 인증 ID
    }
    
    try:
        response = requests.get(url, params=params)
        
        print("Response status code:", response.status_code)
        print("Response content:", response.content.decode())
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                return data["data"]
            else:
                print("No item info data found in response.")
        else:
            print(f"Failed to fetch item info. Status code: {response.status_code}")
    
    except json.JSONDecodeError:
        print("JSON decoding error. Response content:", response.content.decode())
    except Exception as e:
        print("Error occurred while fetching item info:", e)
    
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

def save_item_info(item_code):
    new_data = fetch_item_info(item_code)
    
    if new_data:
        try:
            os.makedirs('docs', exist_ok=True)
            with open(f'docs/item_info_{item_code}.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print(f"item_info_{item_code}.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No item info data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        # 파일 이름에 따라 적절히 수정
        subprocess.run(["git", "add", "docs/item_info_*.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update item info data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    # 여기에 원하는 아이템 코드를 입력
    item_code = 'YOUR_ITEM_CODE'  # 예: '111'과 같은 아이템 코드
    save_item_info(item_code)
