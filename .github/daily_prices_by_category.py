import os
import json
import requests

def get_daily_prices_by_category():
    try:
        api_key = os.getenv('KAMIS_KEY')
        url = f"http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&apikey={api_key}&p_returntype=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            with open('docs/daily_prices_by_category.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error fetching daily prices by category: {e}")

if __name__ == "__main__":
    get_daily_prices_by_category()
