from flask import jsonify, make_response
import json

def baseresponse(isSuccess, responseCode, responseMessage, result=None):
    response = {
        "isSuccess": isSuccess,
        "responseCode": responseCode,
        "responseMessage": responseMessage,
        "result": result if isSuccess else None
    }
    response_json = json.dumps(response, ensure_ascii=False)
    return make_response(response_json, responseCode, {"Content-Type": "application/json; charset=utf-8"})