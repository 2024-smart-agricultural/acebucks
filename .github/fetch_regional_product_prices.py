import requests
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import time

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
BASE_URL = "http://www.kamis.or.kr/service/price/xml.do?action=regionalPriceList"

def load_item_codes_from_json(file_path='docs/code_mappings.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'item_mapping' in data:
                item_codes = list(data['item_mapping'].keys())
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

# 지역별 농산물 도소매 가격 정보 가져오기
def fetch_regional_prices():
    item_codes = load_item_codes_from_json('docs/code_mappings.json')
    if not item_codes:
        print("품목 코드 목록을 가져오는 데 실패했습니다.")
        return

    all_data = []

    for item_code in item_codes:
        retry_count = 3  # 최대 3번 재시도

        for attempt in range(retry_count):
            params = {
                'action': 'regionalPriceList',
                'p_cert_key': KAMIS_KEY,
                'p_cert_id': KAMIS_ID,
                'p_returntype': 'xml',
                'p_endday': datetime.now().strftime('%Y-%m-%d'),
                'p_itemcode': item_code,
                'p_kindcode': '',
                'p_productrankcode': '',
                'p_countycode': ''
            }

            try:
                response = requests.get(BASE_URL, params=params, timeout=10)
                if response.status_code == 200 and response.content.strip():
                    try:
                        # XML 파싱
                        root = ET.fromstring(response.content)
                        items = root.findall('.//item')
                        for item in items:
                            data = {
                                'countyname': item.find('countyname').text if item.find('countyname') is not None else '',
                                'itemname': item.find('itemname').text if item.find('itemname') is not None else '',
                                'kindname': item.find('kindname').text if item.find('kindname') is not None else '',
                                'unit': item.find('unit').text if item.find('unit') is not None else '',
                                'price': item.find('price').text if item.find('price') is not None else '',
                                'weekprice': item.find('weekprice').text if item.find('weekprice') is not None else '',
                                'monthprice': item.find('monthprice').text if item.find('monthprice') is not None else '',
                                'yearprice': item.find('yearprice').text if item.find('yearprice') is not None else ''
                            }
                            # 데이터를 추가할 때, 공백이 아닌 데이터만 저장
                            if any(value for value in data.values()):
                                all_data.append(data)

                        break  # 성공하면 재시도 루프 종료
                    except ET.ParseError:
                        print(f"XML 응답을 파싱할 수 없습니다 (품목 코드: {item_code}). 응답 내용: {response.text}")
                        break  # XML 파싱 오류는 재시도하지 않음
                else:
                    print(f"API 요청 실패 (품목 코드: {item_code}, 시도 횟수: {attempt + 1}): 상태 코드 {response.status_code}")
                    if attempt < retry_count - 1:
                        time.sleep(5)  # 재시도 전에 5초 대기
                    else:
                        print(f"최대 재시도 횟수 초과 (품목 코드: {item_code})")

            except requests.exceptions.RequestException as e:
                print(f"요청 오류 발생 (품목 코드: {item_code}, 시도 횟수: {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(5)
                else:
                    print(f"최대 재시도 횟수 초과 (품목 코드: {item_code})")

        # 각 요청 사이에 딜레이 추가
        time.sleep(2)

    # 기존 JSON 파일 불러오기 또는 새로운 파일 생성
    json_file_path = 'docs/regional_product_prices.json'
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    # 중복 데이터 제거 및 새로운 데이터 추가
    for new_data in all_data:
        if new_data not in existing_data:
            existing_data.append(new_data)

    # 업데이트된 데이터를 JSON 파일로 저장
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    except ValueError as e:
        print(f"JSON 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    fetch_regional_prices()
