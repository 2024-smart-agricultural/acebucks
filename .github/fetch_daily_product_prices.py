import requests
import json
import os
from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
BASE_URL = "http://www.kamis.or.kr/service/price/xml.do?action=periodProductList"

excluded_item_codes = ['161', '113', '162', '163', '164', '114', '216', '248', '261', '262', '263', '264', '265', '217', '218', '266', '318', '319', '321', '322', '423', '426', '427', '430', '429', '614', '650', '651', '652', '612']

def load_item_codes_from_json(file_path='docs/code_mappings.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'item_mapping' in data:
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

def fetch_daily_product_prices():
    item_codes = load_item_codes_from_json('docs/code_mappings.json')
    if not item_codes:
        print("품목 코드 목록을 가져오는 데 실패했습니다.")
        return

    all_data = []

    for item_code in item_codes:
        retry_count = 3

        for attempt in range(retry_count):
            params = {
                'action': 'periodProductList',
                'p_cert_key': KAMIS_KEY,
                'p_cert_id': KAMIS_ID,
                'p_returntype': 'xml',
                'p_startday': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'p_endday': datetime.now().strftime('%Y-%m-%d'),
                'p_itemcode': item_code
            }

            try:
                response = requests.get(BASE_URL, params=params, timeout=10)
                if response.status_code == 200 and response.content.strip():
                    try:
                        root = ET.fromstring(response.content)
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
                            if any(value for value in data.values()):
                                all_data.append(data)
                        break
                    except ET.ParseError:
                        print(f"XML 응답을 파싱할 수 없습니다 (품목 코드: {item_code}). 응답 내용: {response.text}")

                else:
                    print(f"API 요청 실패 (품목 코드: {item_code}, 시도 횟수: {attempt + 1}): 상태 코드 {response.status_code}")
                    if response.status_code == 500:
                        excluded_item_codes.append(item_code)
                        print(f"품목 코드 {item_code}가 서버 오류로 인해 제외되었습니다.")
                        break
                    if attempt < retry_count - 1:
                        time.sleep(2)
                    else:
                        print(f"최대 재시도 횟수 초과 (품목 코드: {item_code})")

            except requests.exceptions.RequestException as e:
                print(f"요청 오류 발생 (품목 코드: {item_code}, 시도 횟수: {attempt + 1}): {e}")

        time.sleep(1)

    json_file_path = 'docs/daily_product_prices.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    for new_data in all_data:
        if new_data not in existing_data:
            existing_data.append(new_data)

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    except ValueError as e:
        print(f"JSON 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    fetch_daily_product_prices()
