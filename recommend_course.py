import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
from bson import ObjectId
from base_response import baseresponse  

# 거리 계산 함수 (반경 필터링)
def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # 지구 반지름 (km)
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c * 1000  # meters

# 반경 내 후보지를 필터링
def filter_by_radius(user_longitude, user_latitude, radius, area_data):
    distances = area_data.apply(lambda row: haversine(user_longitude, user_latitude, row['LONGITUDE'], row['LATITUDE']), axis=1)
    return area_data[distances <= radius]

# 추천 생성 함수
def generate_recommendations(user_input, df, model):
    area_names = df[['VISIT_AREA_NM']].drop_duplicates()
    filtered_area_data = filter_by_radius(user_input['LONGITUDE'], user_input['LATITUDE'], user_input['RADIUS'], df)
    filtered_area_names = filtered_area_data[['VISIT_AREA_NM']].drop_duplicates()
    final_area_names = pd.merge(area_names, filtered_area_names, on='VISIT_AREA_NM')

    user_data = {
        'VISIT_AREA_TYPE_CD': user_input['VISIT_AREA_TYPE_CD'],
        'REVISIT_YN': 'Y',
        'REVISIT_INTENTION': 5,
        'RCMDTN_INTENTION': 5,
        'GENDER': user_input['GENDER'],
        'AGE_GRP': user_input['AGE_GRP'],
        'TRAVEL_STYL_1': user_input['TRAVEL_STYL_1'],
        'TRAVEL_STYL_2': user_input['TRAVEL_STYL_2'],
        'TRAVEL_STYL_3': user_input['TRAVEL_STYL_3'],
        'TRAVEL_STYL_4': user_input['TRAVEL_STYL_4'],
        'TRAVEL_STYL_5': user_input['TRAVEL_STYL_5'],
        'TRAVEL_STYL_6': user_input['TRAVEL_STYL_6'],
        'TRAVEL_STATUS_ACCOMPANY': user_input['TRAVEL_STATUS_ACCOMPANY']
    }

    result = pd.DataFrame([], columns=['AREA_NM', 'SCORE'])
    for area_nm in final_area_names['VISIT_AREA_NM']:
        input_data = [area_nm] + list(user_data.values())
        try:
            score = model.predict(input_data, thread_count=1)
        except Exception as e:
            print(f"Prediction error: {e}")
            return baseresponse(False, 500, "Prediction failed")
        result = pd.concat([result, pd.DataFrame([[area_nm, score]], columns=['AREA_NM', 'SCORE'])])

    return result.sort_values('SCORE', ascending=False).head(10)

# ObjectId 변환 함수
def convert_object_id(data):
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    elif isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in data.items()}
    return data