from flask import jsonify, make_response
import json

def baseresponse(isSuccess, responseCode, responseMessage, result=None):
    response = {
        "isSuccess": isSuccess,
        "responseCode": responseCode,
        "responseMessage": responseMessage,
        "result": result if isSuccess else None
    }

    return make_response(response, responseCode, {"Content-Type": "application/json; charset=utf-8"})

