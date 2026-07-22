from flask import Blueprint, Response, jsonify, request
from flask_login import current_user, login_required

from auth import admin_required
from controllers.problem_group_controller import (
    create_problem_group,
    delete_problem_group,
    get_problem_group,
    update_problem_group,
)
from controllers.ticket_controller import (
    analyze_ticket,
    assign_ticket_to_user,
    create_ticket,
    create_ticket_comment,
    delete_ticket,
    export_tickets,
    get_history_tickets,
    get_ticket_activity,
    get_ticket_by_id,
    get_ticket_comments,
    get_ticket_history,
    get_ticket_metrics,
    get_ticket_metrics_summary,
    get_tickets,
    update_ticket,
)
from services.similarity_service import get_problem_updates, group_problem_tickets, suggest_group_assignment


tickets_bp = Blueprint("tickets", __name__)


def json_result(result, success_status=200):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result), success_status


def _is_admin():
    return current_user.is_authenticated and current_user.role == "admin"


def _ticket_access(ticket_id):
    """Return (ticket, error_response). Regular users may access only their own tickets."""
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return None, (jsonify({"error": "ticket not found"}), 404)
    if not _is_admin() and int(ticket.get("user_id") or 0) != int(current_user.id):
        return None, (jsonify({"error": "access denied for this ticket"}), 403)
    return ticket, None


@tickets_bp.route("", methods=["GET"])
@login_required
def list_tickets():
    filters = {}
    for key in ("statut", "priorite", "departement", "user_id", "groupe_id"):
        value = request.args.get(key)
        if value not in (None, ""):
            filters[key] = value

    # A regular user's dashboard is strictly scoped to their own tickets.
    if not _is_admin():
        filters["user_id"] = current_user.id
    return jsonify(get_tickets(filters=filters))


@tickets_bp.route("/metrics", methods=["GET"])
@admin_required
def ticket_metrics_route():
    return jsonify(get_ticket_metrics())


@tickets_bp.route("/metrics-summary", methods=["GET"])
@admin_required
def ticket_metrics_summary_route():
    return jsonify(get_ticket_metrics_summary())


@tickets_bp.route("/ai-analysis", methods=["POST"])
@login_required
def ai_analysis_route():
    data = request.get_json(silent=True) or {}
    return jsonify(analyze_ticket(data))


@tickets_bp.route("/problem-groups", methods=["GET"])
@admin_required
def problem_groups_route():
    return jsonify(group_problem_tickets())


@tickets_bp.route("/problem-groups", methods=["POST"])
@admin_required
def create_problem_group_route():
    return json_result(create_problem_group(request.get_json(silent=True) or {}), success_status=201)


@tickets_bp.route("/problem-groups/<int:group_id>", methods=["GET"])
@admin_required
def get_problem_group_route(group_id):
    group = get_problem_group(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), 404
    return jsonify(group)


@tickets_bp.route("/problem-groups/<int:group_id>", methods=["PUT"])
@admin_required
def update_problem_group_route(group_id):
    return json_result(update_problem_group(group_id, request.get_json(silent=True) or {}))


@tickets_bp.route("/problem-groups/<int:group_id>", methods=["DELETE"])
@admin_required
def delete_problem_group_route(group_id):
    return json_result(delete_problem_group(group_id))


@tickets_bp.route("/problem-updates", methods=["GET"])
@admin_required
def problem_updates_route():
    problem_group_id = request.args.get("group_id", type=int)
    return jsonify(get_problem_updates(problem_group_id))


@tickets_bp.route("/problem-groups/<int:group_id>/suggest-assignee", methods=["GET", "POST"])
@admin_required
def problem_group_suggest_assignee_route(group_id):
    return json_result(suggest_group_assignment(group_id))


@tickets_bp.route("/history", methods=["GET"])
@admin_required
def history_tickets_route():
    return jsonify(get_history_tickets())


@tickets_bp.route("/export", methods=["GET"])
@admin_required
def export_tickets_route():
    fmt = request.args.get("format", "csv").lower()
    if fmt not in {"csv", "json"}:
        return jsonify({"error": "unsupported export format"}), 400
    payload = export_tickets(format=fmt)
    if fmt == "json":
        return jsonify(payload)
    return Response(
        payload,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tickets.csv"},
    )


@tickets_bp.route("", methods=["POST"])
@login_required
def create_ticket_route():
    payload = dict(request.get_json(silent=True) or {})
    if not _is_admin():
        # For this demo, user_id represents the owner/requester displayed in "Mes demandes".
        payload["user_id"] = current_user.id
        payload["groupe_id"] = None
        payload["statut"] = "ouvert"
    result = create_ticket(payload, actor_user_id=current_user.id)
    return json_result(result, success_status=201)


@tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@login_required
def get_ticket_route(ticket_id):
    ticket, error = _ticket_access(ticket_id)
    if error:
        return error
    return jsonify(ticket)


@tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@login_required
def update_ticket_route(ticket_id):
    _, error = _ticket_access(ticket_id)
    if error:
        return error

    payload = dict(request.get_json(silent=True) or {})
    if not _is_admin():
        allowed_user_fields = {"titre", "description", "statut"}
        payload = {key: value for key, value in payload.items() if key in allowed_user_fields}
        if not payload:
            return jsonify({"error": "no editable user fields supplied"}), 400
    return json_result(update_ticket(ticket_id, payload, actor_user_id=current_user.id))


@tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@admin_required
def delete_ticket_route(ticket_id):
    return json_result(delete_ticket(ticket_id, actor_user_id=current_user.id))


@tickets_bp.route("/<int:ticket_id>/assign", methods=["POST"])
@admin_required
def assign_ticket_route(ticket_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    if user_id in (None, ""):
        return jsonify({"error": "user_id is required"}), 400
    return json_result(
        assign_ticket_to_user(ticket_id, user_id, group_id=group_id, actor_user_id=current_user.id)
    )


@tickets_bp.route("/<int:ticket_id>/comments", methods=["GET"])
@login_required
def list_ticket_comments_route(ticket_id):
    _, error = _ticket_access(ticket_id)
    if error:
        return error
    return jsonify(get_ticket_comments(ticket_id))


@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@login_required
def create_ticket_comment_route(ticket_id):
    _, error = _ticket_access(ticket_id)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    return json_result(
        create_ticket_comment(ticket_id, current_user.id, data.get("message") or data.get("text")),
        success_status=201,
    )


@tickets_bp.route("/<int:ticket_id>/activity", methods=["GET"])
@login_required
def ticket_activity_route(ticket_id):
    _, error = _ticket_access(ticket_id)
    if error:
        return error
    return jsonify(get_ticket_activity(ticket_id))


@tickets_bp.route("/<int:ticket_id>/history", methods=["GET"])
@login_required
def ticket_history_route(ticket_id):
    _, error = _ticket_access(ticket_id)
    if error:
        return error
    return jsonify(get_ticket_history(ticket_id))
