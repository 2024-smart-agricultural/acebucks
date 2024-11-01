#일별농산물도소매(2번)
import requests
import json
import os
from datetime import datetime

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
BASE_URL = "http://www.kamis.or.kr/service/price/xml.do?action=periodProductList"

# 1. 전체 품목 코드 리스트 가져오기
def fetch_item_codes():
    params = {
        'action': 'ItemCodeList',  # 전체 품목 코드 가져오는 액션
        'p_cert_key': KAMIS_KEY,
        'p_cert_id': KAMIS_ID,
        'p_returntype': 'json'
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        item_codes = [item['p_itemcode'] for item in data['itemList']]
        return item_codes
    else:
        print(f"전체 품목 코드 요청 실패: 상태 코드 {response.status_code}")
        return []

# 2. 각 품목에 대한 가격 정보 가져오기
def fetch_daily_prices():
    item_codes = fetch_item_codes()
    if not item_codes:
        print("품목 코드 목록을 가져오는 데 실패했습니다.")
        return

    all_data = []

    for item_code in item_codes:
        params = {
            'action': 'periodProductList',
            'p_cert_key': KAMIS_KEY,
            'p_cert_id': KAMIS_ID,
            'p_returntype': 'json',
            'p_endday': datetime.now().strftime("%Y-%m-%d"),  # 현재 날짜를 종료 날짜로 설정
            'p_itemcode': item_code  # 각 품목 코드에 대해 반복 요청
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()

            # 특정 키 제거
            def remove_keys(obj, keys_to_remove):
                if isinstance(obj, list):
                    return [remove_keys(i, keys_to_remove) for i in obj]
                elif isinstance(obj, dict):
                    return {k: remove_keys(v, keys_to_remove) for k, v in obj.items() if k not in keys_to_remove}
                else:
                    return obj

            keys_to_remove = ['p_cert_key', 'p_cert_id', 'p_startday', 'p_key', 'p_id']
            cleaned_data = remove_keys(data, keys_to_remove)

            # NaN 값 또는 문자열 "null"을 None으로 변환
            def replace_invalid_values(obj):
                if isinstance(obj, list):
                    return [replace_invalid_values(i) for i in obj]
                elif isinstance(obj, dict):
                    return {k: replace_invalid_values(v) for k, v in obj.items()}
                elif isinstance(obj, float) and np.isnan(obj):
                    return None
                elif isinstance(obj, str) and obj.lower() == "null":
                    return None
                else:
                    return obj

            cleaned_data = replace_invalid_values(cleaned_data)

            # 수집된 데이터를 리스트에 추가
            all_data.append(cleaned_data)
        else:
            print(f"API 요청 실패 (품목 코드: {item_code}): 상태 코드 {response.status_code}")
    
    # 기존 JSON 파일 불러오기 또는 새로운 파일 생성
    json_file_path = 'docs/daily_product_prices.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        # 기존 데이터에 새로운 데이터 추가 (중복되지 않는 경우)
        for new_data in all_data:
            if new_data not in existing_data:
                existing_data.append(new_data)
    else:
        existing_data = all_data

    # 업데이트된 데이터를 JSON 파일로 저장
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    fetch_daily_prices()
