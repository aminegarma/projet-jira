import re
import sqlite3

from werkzeug.security import generate_password_hash

from database.db import get_db

ALLOWED_ROLES = {"admin", "manager", "user"}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _public_user(row):
    if row is None:
        return None
    data = dict(row)
    data.pop("password_hash", None)
    data["active"] = bool(data.get("active", 1))
    return data


def validate_user_data(data, partial=False):
    data = data or {}
    errors = {}
    if not partial or "nom" in data:
        if not str(data.get("nom") or "").strip():
            errors["nom"] = "Le nom est obligatoire."
    if not partial or "email" in data:
        email = str(data.get("email") or "").strip().lower()
        if not email:
            errors["email"] = "L'email est obligatoire."
        elif not EMAIL_PATTERN.match(email):
            errors["email"] = "Adresse email invalide."
    if "role" in data and str(data.get("role") or "user").lower() not in ALLOWED_ROLES:
        errors["role"] = "Rôle invalide."
    if data.get("password") and len(str(data["password"])) < 6:
        errors["password"] = "Le mot de passe doit contenir au moins 6 caractères."
    return errors


def create_user(data):
    data = data or {}
    errors = validate_user_data(data, partial=False)
    if errors:
        return {"error": "validation error", "fields": errors}, 400

    email = str(data["email"]).strip().lower()
    password_hash = generate_password_hash(str(data["password"])) if data.get("password") else None
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (nom, email, password_hash, poste, departement, role, active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(data["nom"]).strip(),
                email,
                password_hash,
                str(data.get("poste") or "").strip() or None,
                str(data.get("departement") or "").strip() or None,
                str(data.get("role") or "user").lower(),
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        user_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return {"error": "email already exists"}, 409
    conn.close()
    return {"id": user_id, "message": "user created", "user": _public_user(row)}


def get_users():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nom, email, poste, departement, role, active, date_creation FROM users ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [_public_user(row) for row in rows]


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, nom, email, poste, departement, role, active, date_creation FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return _public_user(row)


def update_user(user_id, data, current_user_id=None):
    data = data or {}
    allowed = {"nom", "email", "poste", "departement", "role", "active", "password"}
    updates = {key: data[key] for key in allowed if key in data}
    if not updates:
        return {"error": "no valid fields supplied"}, 400

    errors = validate_user_data(updates, partial=True)
    if errors:
        return {"error": "validation error", "fields": errors}, 400

    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if existing is None:
        conn.close()
        return {"error": "user not found"}, 404

    if "email" in updates:
        updates["email"] = str(updates["email"]).strip().lower()
        duplicate = conn.execute(
            "SELECT id FROM users WHERE lower(email) = lower(?) AND id != ?",
            (updates["email"], user_id),
        ).fetchone()
        if duplicate:
            conn.close()
            return {"error": "email already exists"}, 409
    if "nom" in updates:
        updates["nom"] = str(updates["nom"]).strip()
    if "role" in updates:
        updates["role"] = str(updates["role"]).lower()
    if "active" in updates:
        updates["active"] = 1 if bool(updates["active"]) else 0
    for field in ("poste", "departement"):
        if field in updates:
            updates[field] = str(updates[field] or "").strip() or None
    if "password" in updates:
        password = str(updates.pop("password") or "")
        if password:
            updates["password_hash"] = generate_password_hash(password)

    if int(current_user_id or 0) == int(user_id):
        if updates.get("active") == 0:
            conn.close()
            return {"error": "you cannot deactivate your own account"}, 400
        if "role" in updates and updates["role"] != "admin":
            conn.close()
            return {"error": "you cannot remove your own administrator role"}, 400

    fields = ", ".join(f"{field} = ?" for field in updates)
    conn.execute(f"UPDATE users SET {fields} WHERE id = ?", list(updates.values()) + [user_id])
    conn.commit()
    row = conn.execute(
        "SELECT id, nom, email, poste, departement, role, active, date_creation FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return {"message": "user updated", "user": _public_user(row)}


def delete_user(user_id, current_user_id=None):
    if int(current_user_id or 0) == int(user_id):
        return {"error": "you cannot delete your own account"}, 400
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if existing is None:
        conn.close()
        return {"error": "user not found"}, 404
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"id": user_id, "message": "user deleted"}


def analyze_selected_users(user_ids):
    if not user_ids:
        return {"message": "no users selected", "selected_users": []}

    conn = get_db()
    placeholders = ", ".join("?" for _ in user_ids)
    users = conn.execute(
        f"SELECT id, nom, departement, poste, role FROM users WHERE id IN ({placeholders}) ORDER BY id",
        user_ids,
    ).fetchall()
    tickets = conn.execute(
        f"SELECT id, titre, categorie, departement_cible, statut, user_id FROM tickets WHERE user_id IN ({placeholders}) ORDER BY id DESC",
        user_ids,
    ).fetchall()
    conn.close()

    selected_users = [dict(user) for user in users]
    related_tickets = [dict(ticket) for ticket in tickets]
    by_department = {}
    categories = {}
    for user in selected_users:
        by_department[user["departement"]] = by_department.get(user["departement"], 0) + 1
    for ticket in related_tickets:
        categories[ticket["categorie"]] = categories.get(ticket["categorie"], 0) + 1

    return {
        "message": "users analyzed",
        "selected_users": selected_users,
        "related_tickets": related_tickets,
        "summary": {
            "user_count": len(selected_users),
            "departments": by_department,
            "ticket_categories": categories,
            "open_tickets": sum(1 for t in related_tickets if t["statut"] == "ouvert"),
            "in_progress_tickets": sum(1 for t in related_tickets if t["statut"] == "en_cours"),
        },
    }
