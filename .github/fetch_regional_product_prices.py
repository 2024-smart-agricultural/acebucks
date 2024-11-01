import aiohttp
import asyncio
import requests
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import time

KAMIS_KEY = os.getenv("KAMIS_KEY")
KAMIS_ID = os.getenv("P_CERT_ID")
BASE_URL = "http://www.kamis.or.kr/service/price/xml.do?action=regionalPriceList"

# URL에서 JSON 파일을 불러오기
def load_item_codes_from_url(url='https://2024-smart-agricultural.github.io/acebucks/code_mappings.json'):
    print(f"URL 확인: {url}")  # URL 출력
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공했는지 확인
        data = response.json()
        print(f"JSON 데이터 로드 성공: {data}")  # JSON 데이터 로드 성공 시 출력
        if 'item_mapping' in data:
            item_codes = list(data['item_mapping'].keys())  # 필터링 없이 모든 품목 코드 사용
            
            # 추가된 디버깅 출력
            print(f"모든 품목 코드: {item_codes}")
            
            return item_codes
        else:
            print(f"'item_mapping' 키를 찾을 수 없습니다. JSON 데이터: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"URL에서 JSON 파일을 불러오는 데 실패했습니다: {e}")
        return []

async def fetch_data(session, item_code):
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
        async with session.get(BASE_URL, params=params, timeout=20) as response:
            if response.status == 200:
                response_text = await response.text()
                try:
                    root = ET.fromstring(response_text)
                    items = root.findall('.//item')
                    data_list = []
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
                        if any(value for value in data.values()):
                            data_list.append(data)
                    return data_list
                except ET.ParseError:
                    print(f"XML 응답을 파싱할 수 없습니다 (품목 코드: {item_code}). 응답 내용: {response_text}")
            elif response.status == 404:
                print(f"품목 코드 {item_code}에 대한 데이터가 없습니다 (상태 코드 404).")
                return None  # 데이터를 제외하도록 None을 반환
            else:
                print(f"API 요청 실패 (품목 코드: {item_code}): 상태 코드 {response.status}")
    except Exception as e:
        print(f"요청 오류 발생 (품목 코드: {item_code}): {e}")
        
async def fetch_all_data(item_codes):
    all_data = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item_code in item_codes:
            tasks.append(fetch_data(session, item_code))
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                all_data.extend(result)

    return all_data

def save_to_json(data, file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    for new_data in data:
        if new_data not in existing_data:
            existing_data.append(new_data)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    except ValueError as e:
        print(f"JSON 저장 중 오류 발생: {e}")

        
def fetch_regional_prices():
    item_codes = load_item_codes_from_url('https://2024-smart-agricultural.github.io/acebucks/code_mappings.json')
    if not item_codes:
        print("품목 코드 목록을 가져오는 데 실패했습니다.")
        return

    all_data = asyncio.run(fetch_all_data(item_codes))
    # 잘못된 부분 수정 ('acebucks/docs/regional_product_prices.json'의 따옴표 누락 수정)
    save_to_json(all_data, 'acebucks/docs/regional_product_prices.json')

if __name__ == "__main__":
    fetch_regional_prices()
