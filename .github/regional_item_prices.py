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

def get_regional_item_prices():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=ItemInfo&apikey={api_key}&p_returntype=xml"  # XML 요청

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            # XML 데이터 파싱
            data = response.text
            parsed_data = parse_xml_data(data)
            filtered_data = filter_desired_items(parsed_data)
            return {
                "all_data": filtered_data,  # 필터링된 데이터 저장
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for regional item prices. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching regional item prices: {e}")
        return None

def parse_xml_data(data):
    import xml.etree.ElementTree as ET
    
    root = ET.fromstring(data)
    items = []

    for item in root.findall(".//item"):
        countyname = item.find("countyname").text
        itemname = item.find("itemname").text
        kindname = item.find("kindname").text
        unit = item.find("unit").text
        price = item.find("price").text
        weekprice = item.find("weekprice").text
        monthprice = item.find("monthprice").text
        yearprice = item.find("yearprice").text
        
        items.append({
            "countyname": countyname,
            "itemname": itemname,
            "kindname": kindname,
            "unit": unit,
            "price": price,
            "weekprice": weekprice,
            "monthprice": monthprice,
            "yearprice": yearprice
        })

    return items

def filter_desired_items(items):
    filtered_items = []
    for item in items:
        item_name = item.get('itemname', '')
        if any(keyword in item_name for keyword in desired_keywords):
            filtered_items.append(item)
    return filtered_items

def save_regional_item_prices():
    new_data = get_regional_item_prices()
    if new_data and new_data['all_data']:
        with open('docs/regional_item_prices.json', 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
        print("regional_item_prices.json created and data saved.")
    else:
        print("No regional item prices data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "you@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Your Name"])

    # JSON 파일을 스테이징
    subprocess.run(["git", "add", "docs/regional_item_prices.json"])

    # 변경 사항이 있을 때만 커밋
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update regional item prices data"])
        subprocess.run(["git", "push"])
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    save_regional_item_prices()
