import os
import sqlite3
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Config.SQLITE_DB_PATH_STR
SCHEMA_PATH = BASE_DIR / "database" / "init_db.sql"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_names(conn, table_name):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _ensure_schema_updates(conn):
    """Apply tiny SQLite migrations without deleting existing demo data."""
    columns = _column_names(conn, "users")
    if "password_hash" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "active" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1")


def _ensure_demo_account(conn, *, name, email, password, role, position, department):
    row = conn.execute(
        "SELECT id, password_hash FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    password_hash = generate_password_hash(password)
    if row is None:
        cursor = conn.execute(
            """
            INSERT INTO users (nom, email, password_hash, poste, departement, role, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (name, email.lower(), password_hash, position, department, role),
        )
        return cursor.lastrowid

    updates = ["role = ?", "active = 1"]
    params = [role]

    # Repair old or incompatible hashes automatically. This is intentional for
    # the local demo accounts so the documented credentials always work.
    stored_hash = row["password_hash"]
    try:
        password_matches = bool(stored_hash) and check_password_hash(stored_hash, password)
    except (TypeError, ValueError):
        password_matches = False

    if not password_matches:
        updates.append("password_hash = ?")
        params.append(password_hash)

    params.append(row["id"])
    conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    return row["id"]


def ensure_demo_accounts(conn):
    _ensure_demo_account(
        conn,
        name="Administrateur Demo",
        email=Config.DEMO_ADMIN_EMAIL,
        password=Config.DEMO_ADMIN_PASSWORD,
        role="admin",
        position="Administrateur",
        department="IT",
    )
    agent_id = _ensure_demo_account(
        conn,
        name="Agent Support Demo",
        email=Config.DEMO_AGENT_EMAIL,
        password=Config.DEMO_AGENT_PASSWORD,
        role="user",
        position="Agent support",
        department="IT",
    )

    # Give the regular demo account a visible first request without overwriting
    # any data the user may already have created.
    has_ticket = conn.execute(
        "SELECT 1 FROM tickets WHERE user_id = ? LIMIT 1", (agent_id,)
    ).fetchone()
    if has_ticket is None:
        cursor = conn.execute(
            """
            INSERT INTO tickets
                (titre, description, categorie, gravite, priorite,
                 departement_cible, statut, user_id, groupe_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                "Demande de démonstration utilisateur",
                "Cette demande permet de tester l'espace utilisateur, les commentaires et le suivi.",
                "support",
                "faible",
                "normal",
                "IT",
                "ouvert",
                agent_id,
            ),
        )
        ticket_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO ticket_history (ticket_id, action) VALUES (?, ?)",
            (ticket_id, "created"),
        )
        conn.execute(
            "INSERT INTO ticket_activity (ticket_id, action, details) VALUES (?, ?, ?)",
            (ticket_id, "ticket_created", '{"source":"demo-user-dashboard"}'),
        )


def init_db(force=False):
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    _ensure_schema_updates(conn)
    ensure_demo_accounts(conn)
    conn.commit()
    conn.close()
    return DB_PATH
