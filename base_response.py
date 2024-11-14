from flask import jsonify, make_response
import json

def baseresponse(isSuccess, responseCode, responseMessage, result=None):
    response = {
        "isSuccess": isSuccess,
        "responseCode": responseCode,
        "responseMessage": responseMessage,
        "result": result if isSuccess else None
    }
    response_json = jsonify(response)
    response = make_response(response_json, responseCode)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

