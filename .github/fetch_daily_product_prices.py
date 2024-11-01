#일별농산물도소매(2번)
import requests
import json
import os
from datetime import datetime

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
URL = "http://www.kamis.or.kr/service/price/xml.do?action=periodProductList"

def fetch_daily_prices():
    params = {
        'p_cert_key': KAMIS_KEY,
        'p_cert_id': KAMIS_ID,
        'p_returntype': 'json',
        'p_endday': datetime.now().strftime("%Y-%m-%d"),  # 현재 날짜를 종료 날짜로 설정
        'p_itemcategorycode': '',  # 모든 품목 카테고리 가져오기
        'p_itemcode': ''  # 모든 품목 코드 가져오기
    }
    
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        data = response.json()
    
        # 기존 JSON 파일 불러오기 또는 새로운 파일 생성
        json_file_path = 'docs/daily_rpoduct_prices.json'
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # 기존 데이터에 새로운 데이터 추가
            existing_data.append(data)
        else:
            existing_data = [data]

        # 업데이트된 데이터를 JSON 파일로 저장
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    else:
        print(f"API 요청 실패: 상태 코드 {response.status_code}")

if __name__ == "__main__":
    fetch_daily_prices()
