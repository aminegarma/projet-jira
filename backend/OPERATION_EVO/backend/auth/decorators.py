from functools import wraps

from flask import jsonify
from flask_login import current_user


def admin_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "authentication required"}), 401
        if current_user.role != "admin":
            return jsonify({"error": "administrator access required"}), 403
        return function(*args, **kwargs)

    return decorated
