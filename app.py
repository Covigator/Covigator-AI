from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World!"

@app.route('/recommend', methods=['POST'])
def recommend():
    
    # JSON 데이터 파싱
    user_data = request.json
    age = user_data.get('age')
    gender = user_data.get('gender')
    travel_style = user_data.get('travel_style')










if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug=True)