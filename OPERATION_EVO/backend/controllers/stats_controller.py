from database.db import get_db


def get_dashboard_stats():
    """Renvoyer les statistiques du tableau de bord."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as count FROM tickets").fetchone()["count"]
    ouverts = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'ouvert'").fetchone()["count"]
    resolves = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'resolu'").fetchone()["count"]
    en_cours = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'en_cours'").fetchone()["count"]
    conn.close()
    return {
        "total_tickets": total,
        "tickets_ouverts": ouverts,
        "tickets_resolus": resolves,
        "tickets_en_cours": en_cours,
    }


def get_periodic_summary(period='month'):
    """Renvoyer un résumé périodique des tickets."""
    conn = get_db()
    rows = conn.execute(
        "SELECT substr(date_creation, 1, 7) as periode, COUNT(*) as total FROM tickets GROUP BY substr(date_creation, 1, 7) ORDER BY periode DESC"
    ).fetchall()
    conn.close()
    return {"period": period, "data": [dict(row) for row in rows]}
