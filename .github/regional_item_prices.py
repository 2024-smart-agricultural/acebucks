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

def get_regional_item_prices():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=ItemInfo&apikey={api_key}&p_returntype=xml"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.text
            parsed_data = parse_xml_data(data)
            filtered_data = filter_desired_items(parsed_data)
            return {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for regional item prices. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching regional item prices: {e}")
        return None

def parse_xml_data(data):
    items = []
    try:
        root = ET.fromstring(data)

        for item in root.findall(".//item"):
            countyname = item.find("countyname").text if item.find("countyname") is not None else "N/A"
            itemname = item.find("itemname").text if item.find("itemname") is not None else "N/A"
            kindname = item.find("kindname").text if item.find("kindname") is not None else "N/A"
            unit = item.find("unit").text if item.find("unit") is not None else "N/A"
            price = item.find("price").text if item.find("price") is not None else "N/A"
            weekprice = item.find("weekprice").text if item.find("weekprice") is not None else "N/A"
            monthprice = item.find("monthprice").text if item.find("monthprice") is not None else "N/A"
            yearprice = item.find("yearprice").text if item.find("yearprice") is not None else "N/A"

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
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")

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
        try:
            with open('docs/recent_regional_prices.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("recent_regional_prices.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No recent regional prices data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        subprocess.run(["git", "add", "docs/recent_regional_prices.json"], check=True)

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
