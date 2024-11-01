#일별농산물도소매(2번)
import requests
import json
import os
from datetime import datetime
import numpy as np
from datetime import datetime, timedelta  # timedelta를 추가로 가져옴
import time
import xml.etree.ElementTree as ET

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
BASE_URL = "http://www.kamis.or.kr/service/price/xml.do?action=periodProductList"

# 제외하고자 하는 품목 코드 리스트
excluded_item_codes = ['161', '113', '162', '163', '164', '114', '216', '248', '261', '262', '263', '264', '265', '217', '218', '266', '318', '319', '321', '322', '423', '426', '427', '430', '429', '614', '650', '651', '652', '612']

# 제외할 품목 코드 리스트 (초기화)
excluded_item_codes = ['161', '113', '162', '163', '164', '114', '216', '248', '261', '262', '263', '264', '265', '217', '218', '266', '318', '319', '321', '322', '423', '426', '427', '430', '429', '614', '650', '651', '652', '612']

# code_mappings.json 파일에서 전체 품목 코드 리스트 가져오기
def load_item_codes_from_json(file_path='docs/code_mappings.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'item_mapping' in data:
                # 제외할 품목 코드 필터링
                item_codes = [code for code in data['item_mapping'].keys() if code not in excluded_item_codes]
                return item_codes
            else:
                print(f"'item_mapping' 키를 찾을 수 없습니다. JSON 데이터: {data}")
                return []
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"JSON 파일을 파싱할 수 없습니다: {file_path}")
        return []

# NaN 값 또는 문자열 "null"을 None으로 변환하는 함수
def replace_invalid_values(obj):
    if isinstance(obj, list):
        return [replace_invalid_values(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: replace_invalid_values(v) for k, v in obj.items()}
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, str) and obj.lower() == "null":
        return None
    else:
        return obj

# 일별 농산물 도소매 가격 정보 가져오기
def fetch_daily_product_prices():
    item_codes = load_item_codes_from_json('docs/code_mappings.json')
    if not item_codes:
        print("품목 코드 목록을 가져오는 데 실패했습니다.")
        return

    all_data = []

    for item_code in item_codes:
        # 제외된 품목 코드는 아예 실행하지 않음
        if item_code in excluded_item_codes:
            print(f"품목 코드 {item_code}는 제외된 코드입니다. 실행하지 않습니다.")
            continue

        retry_count = 3  # 최대 3번 재시도

        for attempt in range(retry_count):
            params = {
                'action': 'periodProductList',
                'p_cert_key': KAMIS_KEY,
                'p_cert_id': KAMIS_ID,
                'p_returntype': 'xml',  # XML 형식으로 반환 요청
                'p_startday': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # 30일 전부터 시작
                'p_endday': datetime.now().strftime('%Y-%m-%d'),  # 현재 날짜를 종료 날짜로 설정
                'p_itemcode': item_code  # 각 품목 코드에 대해 반복 요청
            }

            response = requests.get(BASE_URL, params=params)

            # XML 응답 처리
            if params['p_returntype'] == 'xml' and response.status_code == 200:
                if response.content.strip():  # 응답이 비어 있지 않은지 확인
                    try:
                        # XML 파싱
                        root = ET.fromstring(response.content)
    
                        # <item> 요소들을 찾아서 필요한 데이터 추출
                        items = root.findall('.//item')
                        for item in items:
                            data = {
                                'itemname': item.find('itemname').text if item.find('itemname') is not None else '',
                                'kindname': item.find('kindname').text if item.find('kindname') is not None else '',
                                'countyname': item.find('countyname').text if item.find('countyname') is not None else '',
                                'marketname': item.find('marketname').text if item.find('marketname') is not None else '',
                                'yyyy': item.find('yyyy').text if item.find('yyyy') is not None else '',
                                'regday': item.find('regday').text if item.find('regday') is not None else '',
                                'price': item.find('price').text if item.find('price') is not None else ''
                            }
                            # 데이터가 비어있지 않으면 추가
                            if any(value for value in data.values()):
                                all_data.append(data)
    
                        break  # 성공하면 재시도 루프 종료
                    except ET.ParseError:
                        print(f"XML 응답을 파싱할 수 없습니다 (품목 코드: {item_code}). 응답 내용: {response.text}")
                else:
                    print(f"서버에서 빈 응답을 반환했습니다 (품목 코드: {item_code}).")
            else:
                print(f"API 요청 실패 (품목 코드: {item_code}, 상태 코드: {response.status_code})")

            # JSON 응답 처리
            elif params['p_returntype'] == 'json' and response.status_code == 200:
                try:
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

                    # NaN 값 및 유효하지 않은 값 변환
                    cleaned_data = replace_invalid_values(cleaned_data)

                    # 수집된 데이터를 리스트에 추가
                    all_data.append(cleaned_data)

                    break  # 성공하면 재시도 루프 종료
                except json.JSONDecodeError:
                    print(f"JSON 응답을 파싱할 수 없습니다 (품목 코드: {item_code}). 응답 내용: {response.text}")

            # 요청 실패 처리
            else:
                print(f"API 요청 실패 (품목 코드: {item_code}, 시도 횟수: {attempt + 1}): 상태 코드 {response.status_code}")
                if response.status_code == 500:
                    excluded_item_codes.append(item_code)  # 실패한 품목 코드 기록하여 이후 실행 시 제외
                    print(f"품목 코드 {item_code}가 서버 오류로 인해 제외되었습니다.")
                    break  # 상태 코드 500인 경우 재시도하지 않음
                if attempt < retry_count - 1:
                    time.sleep(2)  # 재시도 전에 2초 대기
                else:
                    print(f"최대 재시도 횟수 초과 (품목 코드: {item_code})")

        # 각 요청 사이에 딜레이 추가
        time.sleep(1)  # 서버 과부하 방지를 위해 1초 대기

    # 각 요청 사이에 딜레이 추가
        time.sleep(1)  # 서버 과부하 방지를 위해 1초 대기

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
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    except ValueError as e:
        print(f"JSON 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    fetch_daily_product_prices()
