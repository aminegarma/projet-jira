from werkzeug.security import check_password_hash

from database.db import get_db
from models.user import User


def get_user_by_id_for_session(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, nom, email, poste, departement, role, active FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return User.from_row(row)


def authenticate_user(email, password):
    email = str(email or "").strip().lower()
    password = str(password or "")
    if not email or not password:
        return None

    conn = get_db()
    row = conn.execute(
        """
        SELECT id, nom, email, password_hash, poste, departement, role, active
        FROM users
        WHERE lower(email) = lower(?)
        """,
        (email,),
    ).fetchone()
    conn.close()

    if row is None or not row["active"] or not row["password_hash"]:
        return None
    if not check_password_hash(row["password_hash"], password):
        return None
    return User.from_row(row)
