from flask import jsonify

def baseresponse(isSuccess, responseCode, responseMessage, result=None):
    response = {
        "isSuccess": isSuccess,
        "responseCode": responseCode,
        "responseMessage": responseMessage,
        "result": result if isSuccess else None
    }
    return jsonify(response), responseCode

