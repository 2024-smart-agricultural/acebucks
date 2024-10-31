import os
import json
import requests
from datetime import datetime
import subprocess

def get_recent_regional_prices():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.co.kr/service/price/xml.do?action=dailySalesList&p_cert_key={api_key}&p_cert_id={api_key}&p_returntype=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            regional_info = {
                "all_data": data,  # 전체 데이터 저장
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return regional_info
        else:
            print(f"Failed to fetch data for recent regional prices. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching recent regional prices: {e}")
        return None

def save_recent_regional_prices():
    new_data = get_recent_regional_prices()
    if new_data:
        with open('docs/recent_regional_prices.json', 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
        print("recent_regional_prices.json created and data saved.")
    else:
        print("No recent regional prices data collected.")

    commit_and_push_changes()

def commit_and_push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "you@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Your Name"])

    # JSON 파일을 스테이징
    subprocess.run(["git", "add", "docs/recent_regional_prices.json"])

    # 변경 사항이 있을 때만 커밋
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update recent regional prices data"])
        subprocess.run(["git", "push"])
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    save_recent_regional_prices()
