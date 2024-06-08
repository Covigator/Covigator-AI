import requests
import time
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz

BASE_URL = "http://openapi.seoul.go.kr:8088/44434c75716a616534354c774e7959/json/citydata/1/5/"
RETRIES = 5

TIME = 'PPLTN_TIME'
CITY_DATA = 'CITYDATA'
SEOUL_DATA_POPULATION = 'LIVE_PPLTN_STTS'
AREA_NAME = 'AREA_NM'
AREA_CODE = 'AREA_CD'
AREA_CONGEST_LEVEL = 'AREA_CONGEST_LVL'
AREA_POPULATION_MIN = 'AREA_PPLTN_MIN'
AREA_POPULATION_MAX = 'AREA_PPLTN_MAX'
AVERAGE_ROAD_DATA = 'AVG_ROAD_DATA'
ROAD_TRAFFIC_STATUS = 'ROAD_TRAFFIC_STTS'
ROAD_TRAFFIC_SPEED = 'ROAD_TRAFFIC_SPD'
WEATHER_STATUS = 'WEATHER_STTS'
TEMPERATURE = 'TEMP'
HUMIDITY = 'HUMIDITY'
PRECIPITATION = 'PRECIPITATION'
UV_INDEX_LEVEL = 'UV_INDEX_LVL'
PM25 = 'PM25'
PM10 = 'PM10'

def write_data_to_csv(area_name, area_code, congestion_level, population_min, population_max, traffic_speed, temperature, humidity,
                           precipitation, uv_level, pm25, pm10, file_path):

    fieldnames = ['시각', '지역명', '지역코드', '혼잡도', '최소인구수', '최대인구수', '전체도로소통평균속도', '기온', '습도', '강수량', '자외선지수단계', '초미세먼지농도', '미세먼지농도']

    # 파일이 존재하지 않으면 새로 생성
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    # 데이터 추가
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        seoul_tz = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(seoul_tz).strftime("%Y-%m-%d %H:%M")

        writer.writerow({
            '시각': current_time,
            '지역명': area_name,
            '지역코드': area_code,
            '혼잡도': congestion_level,
            '최소인구수': population_min,
            '최대인구수': population_max,
            '전체도로소통평균속도': traffic_speed,
            '기온': temperature,
            '습도': humidity,
            '강수량': precipitation,
            '자외선지수단계': uv_level,
            '초미세먼지농도': pm25,
            '미세먼지농도': pm10
        })

def request_data(area_code):
    retry_count = 0

    while retry_count < RETRIES:
        try:
            response = requests.get(BASE_URL + area_code)
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                return data

        except requests.exceptions.HTTPError as err:
            print("HTTP 오류가 발생했습니다:", err)
        except requests.exceptions.RequestException as err:
            print("요청 예외가 발생했습니다:", err)

        retry_count += 1
        time.sleep(3)  # 재시도 전 대기

    return None

def do_thread_collect(i):
    poi_number = str(i).zfill(3)
    area_code = 'POI' + poi_number
    data = request_data(area_code)

    if data:
        area_name = data[CITY_DATA][AREA_NAME]
        area_code = data[CITY_DATA][AREA_CODE]
        congestion_level = data[CITY_DATA][SEOUL_DATA_POPULATION][0][AREA_CONGEST_LEVEL]
        population_min = data[CITY_DATA][SEOUL_DATA_POPULATION][0][AREA_POPULATION_MIN]
        population_max = data[CITY_DATA][SEOUL_DATA_POPULATION][0][AREA_POPULATION_MAX]
        traffic_speed = data[CITY_DATA][ROAD_TRAFFIC_STATUS][AVERAGE_ROAD_DATA][ROAD_TRAFFIC_SPEED]
        temperature = data[CITY_DATA][WEATHER_STATUS][0][TEMPERATURE]
        humidity = data[CITY_DATA][WEATHER_STATUS][0][HUMIDITY]
        precipitation = data[CITY_DATA][WEATHER_STATUS][0][PRECIPITATION]
        uv_level = data[CITY_DATA][WEATHER_STATUS][0][UV_INDEX_LEVEL]
        pm25 = data[CITY_DATA][WEATHER_STATUS][0][PM25]
        pm10 = data[CITY_DATA][WEATHER_STATUS][0][PM10]

        if precipitation == '-': precipitation = 0

        data_folder = os.path.join(os.getcwd(), 'popularity', 'data')
        file_path = os.path.join(data_folder, f'{area_name}.csv')

        write_data_to_csv(area_name, area_code, congestion_level, population_min, population_max, traffic_speed, temperature, humidity,
                           precipitation, uv_level, pm25, pm10, file_path)

def main():

    start_time = time.time()  # 실행 시간 측정 시작

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(do_thread_collect, range(1, 116))

    end_time = time.time()
    execution_time = end_time - start_time
    print("총 실행 시간:", execution_time, "초")

if __name__ == '__main__':
    main()