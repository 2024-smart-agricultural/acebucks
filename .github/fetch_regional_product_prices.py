#지역별 농산물 도소매 가격(14번)
import requests
import json
import os
from datetime import datetime

KAMIS_KEY = os.getenv("KAMIS_KEY")
URL = "https://www.kamis.or.kr/service/price/xml.do"  # 실제 KAMIS 지역별 가격 정보 API 엔드포인트로 변경

def fetch_regional_prices():
    params = {
        'action': 'regionalPriceList',
        'p_cert_key': KAMIS_KEY,
        'p_cert_id': 'your_id',
        'p_returntype': 'json',
        # 필요한 추가 파라미터
    }
    response = requests.get(URL, params=params)
    data = response.json()

    # /docs 디렉토리에 JSON 파일로 저장
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f'docs/regional_product_prices_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_regional_prices()
