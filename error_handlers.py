from flask import jsonify
import logging

# 로깅 설정
logging.basicConfig(filename='error.log', level=logging.ERROR)

def error_response(status_code, message):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response

def register_error_handlers(app):
    # 400 Bad Request 핸들러
    @app.errorhandler(400)
    def bad_request_error(e):
        return error_response(400, "Bad Request: " + str(e))

    # 404 Not Found 핸들러
    @app.errorhandler(404)
    def not_found_error(e):
        return error_response(404, "Not Found: " + str(e))

    # 500 Internal Server Error 핸들러
    @app.errorhandler(500)
    def internal_server_error(e):
        logging.error("Server error occurred", exc_info=True)
        return error_response(500, "An internal server error occurred")