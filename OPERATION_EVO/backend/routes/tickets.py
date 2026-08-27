from flask import Blueprint, Response, jsonify, request
from flask_login import current_user, login_required

from auth import admin_required, manager_or_admin_required
from controllers.problem_group_controller import (
    create_problem_group,
    delete_problem_group,
    get_problem_group,
    update_problem_group,
)
from controllers.ticket_controller import (
    analyze_ticket,
    analyze_ticket_jira_payload,
    assign_ticket_to_user,
    create_ticket,
    create_ticket_comment,
    delete_ticket,
    export_custom_table,
    export_tickets,
    export_history_tickets,
    export_history_ticket_item,
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


def _is_manager_or_admin():
    return current_user.is_authenticated and str(current_user.role).lower() in {"admin", "manager"}


def _export_response(payload, fmt, base_filename):
    if fmt == "pdf":
        return Response(
            payload,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={base_filename}.pdf"},
        )
    if fmt == "excel":
        return Response(
            payload,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={base_filename}.xlsx"},
        )
    return Response(
        payload,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={base_filename}.csv"},
    )


def _ticket_access(ticket_id):
    """Return (ticket, error_response). Regular users may access only their own tickets."""
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return None, (jsonify({"error": "ticket not found"}), 404)
    if not _is_manager_or_admin() and int(ticket.get("user_id") or 0) != int(current_user.id):
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
    if not _is_manager_or_admin():
        filters["user_id"] = current_user.id
    return jsonify(get_tickets(filters=filters))


@tickets_bp.route("/metrics", methods=["GET"])
@manager_or_admin_required
def ticket_metrics_route():
    return jsonify(get_ticket_metrics())


@tickets_bp.route("/metrics-summary", methods=["GET"])
@manager_or_admin_required
def ticket_metrics_summary_route():
    return jsonify(get_ticket_metrics_summary())


@tickets_bp.route("/ai-analysis", methods=["POST"])
@login_required
def ai_analysis_route():
    data = request.get_json(silent=True) or {}
    return jsonify(analyze_ticket(data))


@tickets_bp.route("/<int:ticket_id>/ai-problem-solving", methods=["GET"])
@manager_or_admin_required
def ai_problem_solving_route(ticket_id):
    entity = request.args.get("entity")
    result = analyze_ticket_jira_payload(ticket_id, entity=entity)
    return json_result(result)


@tickets_bp.route("/problem-groups", methods=["GET"])
@manager_or_admin_required
def problem_groups_route():
    return jsonify(group_problem_tickets())


@tickets_bp.route("/problem-groups", methods=["POST"])
@admin_required
def create_problem_group_route():
    return json_result(create_problem_group(request.get_json(silent=True) or {}), success_status=201)


@tickets_bp.route("/problem-groups/<int:group_id>", methods=["GET"])
@manager_or_admin_required
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
@manager_or_admin_required
def problem_updates_route():
    problem_group_id = request.args.get("group_id", type=int)
    return jsonify(get_problem_updates(problem_group_id))


@tickets_bp.route("/problem-groups/<int:group_id>/suggest-assignee", methods=["GET", "POST"])
@manager_or_admin_required
def problem_group_suggest_assignee_route(group_id):
    return json_result(suggest_group_assignment(group_id))


@tickets_bp.route("/history", methods=["GET"])
@manager_or_admin_required
def history_tickets_route():
    return jsonify(get_history_tickets())


@tickets_bp.route("/export", methods=["GET"])
@manager_or_admin_required
def export_tickets_route():
    fmt = request.args.get("format", "excel").lower()
    if fmt not in {"excel", "csv", "pdf"}:
        return jsonify({"error": "unsupported export format"}), 400
    try:
        payload = export_tickets(format=fmt)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return _export_response(payload, fmt, "tickets")


@tickets_bp.route("/export/custom", methods=["GET"])
@manager_or_admin_required
def export_custom_route():
    fmt = request.args.get("format", "excel").lower()
    table = request.args.get("table", "tickets")
    fields = request.args.get("fields", "")
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order", "desc")
    if fmt not in {"excel", "csv", "pdf"}:
        return jsonify({"error": "unsupported export format"}), 400

    filters = {}
    for key, value in request.args.items():
        if key.startswith("f_") and value not in (None, ""):
            filters[key[2:]] = value

    try:
        payload = export_custom_table(
            table=table,
            fields=fields,
            sort_by=sort_by,
            sort_order=sort_order,
            format=fmt,
            filters=filters,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return _export_response(payload, fmt, f"{table}_custom_export")


@tickets_bp.route("/history/export", methods=["GET"])
@manager_or_admin_required
def export_history_tickets_route():
    fmt = request.args.get("format", "excel").lower()
    if fmt not in {"excel", "csv", "pdf"}:
        return jsonify({"error": "unsupported export format"}), 400
    try:
        payload = export_history_tickets(format=fmt)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return _export_response(payload, fmt, "historique_tickets")


@tickets_bp.route("/<int:ticket_id>/history-export", methods=["GET"])
@manager_or_admin_required
def export_history_ticket_item_route(ticket_id):
    fmt = request.args.get("format", "excel").lower()
    if fmt not in {"excel", "csv", "pdf"}:
        return jsonify({"error": "unsupported export format"}), 400

    try:
        payload = export_history_ticket_item(ticket_id, format=fmt)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    if payload is None:
        return jsonify({"error": "ticket not found"}), 404

    return _export_response(payload, fmt, f"ticket_{ticket_id}_history")


@tickets_bp.route("", methods=["POST"])
@login_required
def create_ticket_route():
    if str(current_user.role).lower() != "user":
        return jsonify({"error": "ticket creation is restricted to user dashboard accounts"}), 403

    payload = dict(request.get_json(silent=True) or {})

    # Tickets are created only from the user dashboard and always owned by the current user.
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
@manager_or_admin_required
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
