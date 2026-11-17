from flask import jsonify


def success_response(data=None, message="Success", status=200):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status


def error_response(message, status=400, details=None):
    response = {
        "status": "error",
        "message": message
    }

    if details is not None:
        response["details"] = details

    return jsonify(response), status
