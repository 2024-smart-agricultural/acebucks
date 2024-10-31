#일별농산물도소매
import requests
import json
import os
from datetime import datetime

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
URL = "https://www.kamis.or.kr/service/price/xml.do"  # 실제 KAMIS 일별 가격 정보 API 엔드포인트로 변경

def fetch_daily_prices():
    params = {
        'action': 'periodProductList',
        'p_cert_key': KAMIS_KEY,
        'p_cert_id': KAMIS_ID,
        'p_returntype': 'json',
        # 필요한 추가 파라미터
    }
    response = requests.get(URL, params=params)
    data = response.json()

    # /docs 디렉토리에 JSON 파일로 저장
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f'docs/daily_product_prices_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_daily_prices()
