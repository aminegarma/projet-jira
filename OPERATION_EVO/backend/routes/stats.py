from flask import Blueprint, jsonify

from auth import admin_required
from controllers.stats_controller import get_dashboard_stats, get_periodic_summary

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("", methods=["GET"])
@admin_required
def dashboard_stats():
    return jsonify(get_dashboard_stats())


@stats_bp.route("/periodic", methods=["GET"])
@admin_required
def periodic_summary():
    return jsonify(get_periodic_summary("month"))
