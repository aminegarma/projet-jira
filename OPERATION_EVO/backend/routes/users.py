from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from auth import admin_required, manager_or_admin_required
from controllers.user_controller import (
    analyze_selected_users,
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)

users_bp = Blueprint("users", __name__)


def json_result(result, success_status=200):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result), success_status


@users_bp.route("", methods=["GET"])
@manager_or_admin_required
def list_users():
    return jsonify(get_users())


@users_bp.route("/<int:user_id>", methods=["GET"])
@login_required
def get_user_route(user_id):
    if current_user.role != "admin" and int(current_user.id) != int(user_id):
        return jsonify({"error": "access denied"}), 403
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user)


@users_bp.route("/analyze", methods=["POST"])
@admin_required
def analyze_users_route():
    data = request.get_json(silent=True) or {}
    user_ids = data.get("user_ids") or []
    if not isinstance(user_ids, list):
        user_ids = [user_ids] if user_ids else []
    return jsonify(analyze_selected_users(user_ids))


@users_bp.route("", methods=["POST"])
@admin_required
def create_user_route():
    return json_result(create_user(request.get_json(silent=True) or {}), success_status=201)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user_route(user_id):
    return json_result(update_user(user_id, request.get_json(silent=True) or {}, current_user_id=current_user.id))


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user_route(user_id):
    return json_result(delete_user(user_id, current_user_id=current_user.id))
