from flask import jsonify

def api_response(success=True, message="", data=None, status_code=200):
    """Standardized REST API JSON response builder."""
    payload = {
        'success': success,
        'message': message,
        'data': data
    }
    return jsonify(payload), status_code
