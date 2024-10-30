import requests
import os
import json

def fetch_kamis_data():
    api_key = os.getenv("KAMIS_KEY")
    url = f"https://www.kamis.or.kr/service/KamisService/getDailyPriceData?apikey={api_key}&itemCategoryCode=..."
    response = requests.get(url)

    if response.status_code == 200:
        # 응답이 JSON 형식인지 확인
        try:
            data = response.json()
            with open("docs/kamis_data.json", "w") as f:
                json.dump(data, f)
            print("KAMIS data collected successfully.")
        except ValueError:
            print("응답이 JSON 형식이 아닙니다. HTML 페이지가 반환되었습니다.")
            print(response.text)  # HTML 오류 페이지를 출력하여 문제를 파악
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(response.text)  # 오류 메시지 출력

if __name__ == "__main__":
    fetch_kamis_data()
