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

def fetch_daily_prices_by_category():
    print("Running Daily Prices by Category data collection...")
    
    url = 'http://www.kamis.or.kr/service/price/xml.do?action=dailyPricesByCategoryList'
    params = {
        'p_product_cls_code': '02',  
        'p_category_code': '100',    
        'p_regday': '',              
        'p_convert_kg_yn': 'N',      
        'p_cert_key': 'YOUR_API_KEY',  
        'p_cert_id': 'YOUR_CERT_ID',   
        'p_returntype': 'xml'
    }
    
    try:
        response = requests.get(url, params=params)
        print("Response status code:", response.status_code)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            error_code = root.find(".//error_code")
            if error_code is not None and error_code.text == "200":
                print("Data fetched successfully.")
                
                data_items = []
                for item in root.findall(".//item"):
                    item_name = item.find('item_name').text if item.find('item_name') is not None else 'N/A'
                    price = item.find('price').text if item.find('price') is not None else 'N/A'
                    data_items.append({
                        "item_name": item_name,
                        "price": price
                    })
                return data_items
            else:
                print("Error in response. Error code:", error_code.text if error_code is not None else "Unknown")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print("Error occurred while fetching data:", e)
    
    return []

def filter_data_by_keywords(items):
    filtered_items = []
    for item in items:
        item_name = item.get("item_name", "")
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append(item)
    return filtered_items

def save_daily_prices_by_category():
    all_data = fetch_daily_prices_by_category()
    filtered_data = filter_data_by_keywords(all_data)
    
    if filtered_data:
        try:
            os.makedirs('docs', exist_ok=True)
            with open('docs/daily_prices_by_category.json', 'w', encoding='utf-8') as file:
                json.dump(filtered_data, file, ensure_ascii=False, indent=4)
            print("daily_prices_by_category.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No daily prices by category data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/daily_prices_by_category.json"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
        if result.returncode != 0:  # 변경 사항이 있을 때만 커밋
            subprocess.run(["git", "commit", "-m", "Update daily prices by category data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_daily_prices_by_category()
