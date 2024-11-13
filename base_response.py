from flask import jsonify, make_response

def baseresponse(isSuccess, responseCode, responseMessage, result=None):
    response = {
        "isSuccess": isSuccess,
        "responseCode": responseCode,
        "responseMessage": responseMessage,
        "result": result if isSuccess else None
    }
    return make_response(jsonify(response), responseCode, {"Content-Type": "application/json"})

