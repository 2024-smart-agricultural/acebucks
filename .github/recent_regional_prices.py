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
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailySalesList&apikey={api_key}"

        # 필요한 파라미터 추가
        params = {
            "p_regday": datetime.now().strftime("%Y%m%d"),  # 오늘 날짜
            # 필요한 다른 파라미터 추가
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            # XML 응답 파싱
            root = ET.fromstring(response.content)
            result_code = root.find('.//result_code').text if root.find('.//result_code') is not None else ''

            if result_code == "900":
                print("No data available for the requested date.")
                return None

            items = root.findall('.//item')  # XML 구조에 따라 조정 필요
            filtered_data = filter_desired_prices(items)

            return {
                "all_data": filtered_data,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed to fetch data for recent regional prices. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching recent regional prices: {e}")
        return None


def filter_desired_prices(items):
    filtered_items = []
    for item in items:
        product_name = item.find('productName').text if item.find('productName') is not None else ''
        if any(keyword in product_name for keyword in desired_keywords):
            filtered_items.append({
                "productName": product_name,
                # 필요한 다른 데이터 추가
            })
    return filtered_items

def save_recent_regional_prices():
    new_data = get_recent_regional_prices()
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
            subprocess.run(["git", "commit", "-m", "Update recent regional prices data"], check=True)
            subprocess.run(["git", "push"], check=True)
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    save_recent_regional_prices()
