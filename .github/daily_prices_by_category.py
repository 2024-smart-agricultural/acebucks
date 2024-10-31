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

def get_daily_prices_by_category():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&apikey={api_key}&p_returntype=xml"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            # XML 데이터 파싱
            data = response.text
            parsed_data = parse_xml_data(data)
            filtered_data = filter_data_by_keywords(parsed_data)
            category_info = {
                "all_data": filtered_data,  # 필터링된 데이터 저장
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return category_info
        else:
            print(f"Failed to fetch data for daily prices by category. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching daily prices by category: {e}")
        return None

def parse_xml_data(data):
    items = []
    try:
        root = ET.fromstring(data)

        for item in root.findall(".//item"):
            try:
                item_name = item.find("itemname").text if item.find("itemname") is not None else "N/A"
                kind_name = item.find("kindname").text if item.find("kindname") is not None else "N/A"
                county_name = item.find("countyname").text if item.find("countyname") is not None else "N/A"
                reg_day = item.find("regday").text if item.find("regday") is not None else "N/A"
                price = item.find("price").text if item.find("price") is not None else "N/A"

                items.append({
                    "itemname": item_name,
                    "kindname": kind_name,
                    "countyname": county_name,
                    "regday": reg_day,
                    "price": price
                })
            except Exception as e:
                print(f"Error parsing item data: {e}")

    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")

    return items

def filter_data_by_keywords(items):
    filtered_items = [
        item for item in items
        if any(keyword in item['itemname'] for keyword in desired_keywords)
    ]
    return filtered_items  # 필터링된 품목 리스트 반환

def save_daily_prices_by_category():
    new_data = get_daily_prices_by_category()
    if new_data and new_data['all_data']:
        try:
            with open('docs/daily_prices_by_category.json', 'w', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            print("daily_prices_by_category.json created and data saved.")
            commit_and_push_changes()
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No daily prices by category data collected.")

def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)

        # JSON 파일을 스테이징
        subprocess.run(["git", "add", "docs/daily_prices_by_category.json"], check=True)

        # 변경 사항이 있을 때만 커밋
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update daily prices by category data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_daily_prices_by_category()
