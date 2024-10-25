from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
from recommend_course import generate_recommendations, convert_object_id
from catboost import CatBoostRegressor
import os
from dotenv import load_dotenv
from error_handlers import register_error_handlers
from base_response import baseresponse  

app = Flask(__name__)

load_dotenv()

# 에러 핸들러 등록
register_error_handlers(app)

# MongoDB 연결 설정
mongo_url = os.getenv("MONGO_DB_URL")
client = MongoClient(mongo_url)
db = client["covigator"]
collection = db["place"]

# CatBoost 모델 로드
model = CatBoostRegressor()
model.load_model('model/catboost_model_DGSTFN_1018.cbm')

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World!"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.json
        if not user_input:
            raise baseresponse(False, 400, "No input data provided")
        df = pd.DataFrame(list(collection.find()))
        
        # 추천 생성
        top_10_recommendations = generate_recommendations(user_input, df, model)
        top_10_area_names = top_10_recommendations['AREA_NM'].tolist()

        #MongoDB에서 상위 10개 장소 정보 조회
        top_10_info = collection.find(
            {"VISIT_AREA_NM": {"$in": top_10_area_names}},
            {
                "VISIT_AREA_NM": 1,
                "GUNGU": 1,
                "ROAD_NM_ADDR": 1,
                "LOTNO_ADDR": 1,
                "LONGITUDE": 1,
                "LATITUDE": 1,
                "VISIT_AREA_TYPE_CD": 1,
                "PHONE_NUMBER": 1,
                "OPERATION_HOUR": 1
            }
        )
        top_10_info_df = pd.DataFrame(list(top_10_info))

        # 중복 제거 및 JSON 변환
        unique_recommendations = []
        seen_area_names = set()
        seen_types = set()

        for area_name in top_10_area_names:
            area_info = top_10_info_df[top_10_info_df['VISIT_AREA_NM'] == area_name]
            if not area_info.empty:
                area_type = area_info.iloc[0]['VISIT_AREA_TYPE_CD']
                if area_name not in seen_area_names and area_type not in seen_types:
                    unique_recommendations.append(area_info.iloc[0])
                    seen_area_names.add(area_name)
                    seen_types.add(area_type)

        recommendations = convert_object_id(pd.DataFrame(unique_recommendations).to_dict(orient='records'))
        return baseresponse(True, 200, "Recommendations retrieved successfully", recommendations)
    except ValueError as ve:
        return baseresponse(False, 400, str(ve))
    except Exception as e:
        return baseresponse(False, 500, "An unexpected error occurred")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)