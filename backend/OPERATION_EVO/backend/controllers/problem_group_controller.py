from database.db import get_db

ALLOWED_GROUP_STATUSES = {"ouvert", "en_cours", "resolu"}


def _normalize_status(value):
    return str(value or "").strip().lower().replace(" ", "_").replace("résolu", "resolu")


def get_problem_group(group_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, titre_probleme, ticket_maitre_id, statut, date_creation FROM probleme_groupes WHERE id = ?",
        (group_id,),
    ).fetchone()
    conn.close()
    return None if row is None else dict(row)


def create_problem_group(data):
    data = data or {}
    title = str(data.get("titre_probleme") or data.get("titre") or "").strip()
    status = _normalize_status(data.get("statut") or "ouvert")
    master_ticket_id = data.get("ticket_maitre_id") or None
    if not title:
        return {"error": "validation error", "fields": {"titre_probleme": "Le titre est obligatoire."}}, 400
    if status not in ALLOWED_GROUP_STATUSES:
        return {"error": "validation error", "fields": {"statut": "Statut invalide."}}, 400

    conn = get_db()
    if master_ticket_id is not None and conn.execute("SELECT id FROM tickets WHERE id = ?", (master_ticket_id,)).fetchone() is None:
        conn.close()
        return {"error": "validation error", "fields": {"ticket_maitre_id": "Ticket maître introuvable."}}, 400
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO probleme_groupes (titre_probleme, ticket_maitre_id, statut) VALUES (?, ?, ?)",
        (title, master_ticket_id, status),
    )
    group_id = cursor.lastrowid
    if master_ticket_id is not None:
        conn.execute("UPDATE tickets SET groupe_id = ? WHERE id = ?", (group_id, master_ticket_id))
    conn.commit()
    row = conn.execute("SELECT * FROM probleme_groupes WHERE id = ?", (group_id,)).fetchone()
    conn.close()
    return {"message": "problem group created", "group": dict(row)}


def update_problem_group(group_id, data):
    data = data or {}
    allowed = {"titre_probleme", "statut", "ticket_maitre_id"}
    updates = {key: data[key] for key in allowed if key in data}
    if "titre" in data and "titre_probleme" not in updates:
        updates["titre_probleme"] = data["titre"]
    if not updates:
        return {"error": "no valid fields supplied"}, 400

    if "titre_probleme" in updates:
        updates["titre_probleme"] = str(updates["titre_probleme"] or "").strip()
        if not updates["titre_probleme"]:
            return {"error": "validation error", "fields": {"titre_probleme": "Le titre est obligatoire."}}, 400
    if "statut" in updates:
        updates["statut"] = _normalize_status(updates["statut"])
        if updates["statut"] not in ALLOWED_GROUP_STATUSES:
            return {"error": "validation error", "fields": {"statut": "Statut invalide."}}, 400
    if "ticket_maitre_id" in updates and updates["ticket_maitre_id"] in ("", None):
        updates["ticket_maitre_id"] = None

    conn = get_db()
    existing = conn.execute("SELECT id FROM probleme_groupes WHERE id = ?", (group_id,)).fetchone()
    if existing is None:
        conn.close()
        return {"error": "group not found"}, 404
    if updates.get("ticket_maitre_id") is not None:
        ticket = conn.execute("SELECT id FROM tickets WHERE id = ?", (updates["ticket_maitre_id"],)).fetchone()
        if ticket is None:
            conn.close()
            return {"error": "validation error", "fields": {"ticket_maitre_id": "Ticket maître introuvable."}}, 400

    fields = ", ".join(f"{field} = ?" for field in updates)
    conn.execute(f"UPDATE probleme_groupes SET {fields} WHERE id = ?", list(updates.values()) + [group_id])
    if updates.get("ticket_maitre_id") is not None:
        conn.execute("UPDATE tickets SET groupe_id = ? WHERE id = ?", (group_id, updates["ticket_maitre_id"]))
    conn.commit()
    row = conn.execute("SELECT * FROM probleme_groupes WHERE id = ?", (group_id,)).fetchone()
    conn.close()
    return {"message": "problem group updated", "group": dict(row)}


def delete_problem_group(group_id):
    conn = get_db()
    existing = conn.execute("SELECT id FROM probleme_groupes WHERE id = ?", (group_id,)).fetchone()
    if existing is None:
        conn.close()
        return {"error": "group not found"}, 404
    conn.execute("DELETE FROM probleme_groupes WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()
    return {"id": group_id, "message": "problem group deleted"}
