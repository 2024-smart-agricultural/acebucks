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

def get_recent_regional_prices():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailySalesList&p_cert_key={api_key}&p_returntype=xml"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            # XML 데이터 파싱
            data = response.text
            parsed_data = parse_xml_data(data)
            filtered_data = filter_desired_prices(parsed_data)
            regional_info = {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return regional_info
        else:
            print(f"Failed to fetch data for recent regional prices. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching recent regional prices: {e}")
        return None

def parse_xml_data(data):
    root = ET.fromstring(data)
    items = []

    for item in root.findall(".//item"):
        try:
            county_code = item.find("county_code").text
            county_name = item.find("county_name").text
            product_cls_code = item.find("product_cls_code").text
            product_cls_name = item.find("product_cls_name").text
            category_code = item.find("category_code").text
            category_name = item.find("category_name").text
            productno = item.find("productno").text
            lastest_day = item.find("lastest_day").text
            product_name = item.find("productName").text
            item_name = item.find("item_name").text
            unit = item.find("unit").text
            dpr1 = item.find("dpr1").text
            dpr2 = item.find("dpr2").text
            dpr3 = item.find("dpr3").text
            dpr4 = item.find("dpr4").text
            direction = item.find("direction").text
            value = item.find("value").text

            items.append({
                "county_code": county_code,
                "county_name": county_name,
                "product_cls_code": product_cls_code,
                "product_cls_name": product_cls_name,
                "category_code": category_code,
                "category_name": category_name,
                "productno": productno,
                "lastest_day": lastest_day,
                "productName": product_name,
                "item_name": item_name,
                "unit": unit,
                "dpr1": dpr1,
                "dpr2": dpr2,
                "dpr3": dpr3,
                "dpr4": dpr4,
                "direction": direction,
                "value": value,
            })
        except Exception as e:
            print(f"Error parsing item data: {e}")

    return items

def filter_desired_prices(items):
    filtered_items = []
    for item in items:
        product_name = item.get('productName', '')
        if any(keyword in product_name for keyword in desired_keywords):
            filtered_items.append(item)
    return filtered_items  # 필터링된 품목 리스트 반환

def save_recent_regional_prices():
    new_data = get_recent_regional_prices()
    if new_data and new_data['all_data']:
        try:
            with open('docs/recent_regional_prices.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("recent_regional_prices.json created and data saved.")
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    
        commit_and_push_changes()
    else:
        print("No recent regional prices data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        # JSON 파일을 스테이징
        subprocess.run(["git", "add", "docs/recent_regional_prices.json"], check=True)

        # 변경 사항이 있을 때만 커밋
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update recent regional prices data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_recent_regional_prices()
