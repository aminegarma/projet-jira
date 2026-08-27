from functools import wraps

from flask import jsonify
from flask_login import current_user


def role_required(*roles):
    accepted = {str(role).strip().lower() for role in roles if str(role).strip()}

    def decorator(function):
        @wraps(function)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "authentication required"}), 401

            current_role = str(getattr(current_user, "role", "") or "").lower()
            if current_role not in accepted:
                return jsonify({"error": "insufficient role permissions"}), 403
            return function(*args, **kwargs)

        return decorated

    return decorator


def admin_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "authentication required"}), 401
        if str(current_user.role).lower() != "admin":
            return jsonify({"error": "administrator access required"}), 403
        return function(*args, **kwargs)

    return decorated


def manager_or_admin_required(function):
    return role_required("manager", "admin")(function)
