import requests
import time
import csv
import os
from concurrent.futures import ThreadPoolExecutor


BASE_URL = "http://openapi.seoul.go.kr:8088/44434c75716a616534354c774e7959/json/citydata_ppltn/1/5/"
RETRIES = 5

SEOUL_DATA_POPULATION = 'SeoulRtd.citydata_ppltn'
AREA_NAME = 'AREA_NM'
AREA_CODE = 'AREA_CD'
AREA_CONGEST_LEVEL = 'AREA_CONGEST_LVL'
AREA_POPULATION_MIN = 'AREA_PPLTN_MIN'
AREA_POPULATION_MAX = 'AREA_PPLTN_MAX'

def write_data_to_csv(area_name, area_code, congestion_level, population_min, population_max, file_path):

    fieldnames = ['지역명', '지역 코드', '혼잡도', '최소 인구수', '최대 인구수']

    # 파일이 존재하지 않으면 새로 생성
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    # 데이터 추가
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writerow({
            '지역명': area_name,
            '지역 코드': area_code,
            '혼잡도': congestion_level,
            '최소 인구수': population_min,
            '최대 인구수': population_max
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
        area_name = data[SEOUL_DATA_POPULATION][0][AREA_NAME]
        area_code = data[SEOUL_DATA_POPULATION][0][AREA_CODE]
        congestion_level = data[SEOUL_DATA_POPULATION][0][AREA_CONGEST_LEVEL]
        population_min = data[SEOUL_DATA_POPULATION][0][AREA_POPULATION_MIN]
        population_max = data[SEOUL_DATA_POPULATION][0][AREA_POPULATION_MAX]

        data_folder = os.path.join(os.getcwd(), 'popularity', 'data')
        file_path = os.path.join(data_folder, f'{area_name}.csv')

        write_data_to_csv(area_name, area_code, congestion_level, population_min, population_max, file_path)

def main():

    start_time = time.time()  # 실행 시간 측정 시작

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(do_thread_collect, range(1, 116))

    end_time = time.time()
    execution_time = end_time - start_time
    print("총 실행 시간:", execution_time, "초")

if __name__ == '__main__':
    main()