import re
from database.db import get_db
from services.mistral_service import classify_ticket


def _tokenize(text):
    return set(re.findall(r"[a-zA-ZÀ-ÿ]+", (text or "").lower()))


def build_ai_suggestions(ticket_data):
    """Retourne des suggestions IA basées sur des tickets déjà présents en base, mais uniquement pour aider le frontend à grouper et à mettre à jour."""
    if isinstance(ticket_data, str):
        description = ticket_data
        title = ticket_data
        payload = {"description": description, "titre": title}
    else:
        payload = ticket_data or {}
        description = payload.get("description") or payload.get("titre") or ""
        title = payload.get("titre") or ""

    classification = classify_ticket(description or title)
    keywords = _tokenize(f"{title} {description}")
    conn = get_db()
    rows = conn.execute(
        "SELECT id, titre, description, categorie, gravite, priorite, departement_cible, statut, user_id, groupe_id FROM tickets ORDER BY id DESC"
    ).fetchall()
    users = conn.execute("SELECT id, nom, email, departement FROM users WHERE active = 1 ORDER BY id DESC").fetchall()
    conn.close()

    scored_rows = []
    for row in rows:
        row_text = f"{row['titre']} {row['description'] or ''}"
        row_tokens = _tokenize(row_text)
        score = len(keywords & row_tokens)
        if row['categorie'] == classification.get("categorie"):
            score += 3
        if row['departement_cible'] == classification.get("departement"):
            score += 2
        if score > 0:
            scored_rows.append((score, dict(row)))

    scored_rows.sort(key=lambda item: item[0], reverse=True)
    similar_tickets = []
    for score, row in scored_rows[:5]:
        similar_tickets.append({
            "id": row["id"],
            "titre": row["titre"],
            "categorie": row["categorie"],
            "departement_cible": row["departement_cible"],
            "statut": row["statut"],
            "user_id": row["user_id"],
            "groupe_id": row["groupe_id"],
            "similarity_score": score,
        })

    suggested_users = []
    for user in users:
        user_text = f"{user['nom'] or ''} {user['email'] or ''} {user['departement'] or ''}".lower()
        if classification.get("departement") and classification.get("departement", '').lower() in user_text:
            suggested_users.append({
                "id": user["id"],
                "nom": user["nom"],
                "email": user["email"],
                "departement": user["departement"],
            })
    if not suggested_users:
        suggested_users = [
            {
                "id": user["id"],
                "nom": user["nom"],
                "email": user["email"],
                "departement": user["departement"],
            }
            for user in users[:3]
        ]

    return {
        "classification": classification,
        "similar_tickets": similar_tickets,
        "suggested_department": classification.get("departement"),
        "suggested_users": suggested_users,
        "reason": "Suggestion IA fondée sur l’historique des tickets similaires et les anciens tickets déjà traités dans le même domaine.",
    }


def suggest_group_assignment(group_id):
    """Suggère un utilisateur d’affectation pour un groupe de problèmes à partir de l’historique des tickets similaires."""
    conn = get_db()
    group_row = conn.execute(
        "SELECT id, titre_probleme, statut FROM probleme_groupes WHERE id = ?",
        (group_id,),
    ).fetchone()
    if group_row is None:
        conn.close()
        return {"error": "group not found"}, 404

    group_tickets = conn.execute(
        "SELECT id, titre, description, categorie, departement_cible, statut, user_id FROM tickets WHERE groupe_id = ? ORDER BY id DESC",
        (group_id,),
    ).fetchall()
    history_rows = conn.execute(
        "SELECT id, titre, description, categorie, departement_cible, statut, user_id FROM tickets WHERE user_id IS NOT NULL ORDER BY id DESC"
    ).fetchall()
    users = conn.execute("SELECT id, nom, email, departement FROM users WHERE active = 1 ORDER BY id DESC").fetchall()
    conn.close()

    history_by_user = {}
    for row in history_rows:
        current_user_id = row["user_id"]
        if current_user_id is None:
            continue
        history_by_user.setdefault(current_user_id, []).append(dict(row))

    scored_users = []
    for user in users:
        user_id = user["id"]
        history_items = history_by_user.get(user_id, [])
        score = 0
        evidence = []
        for ticket in group_tickets:
            ticket_dict = dict(ticket)
            ticket_text = _tokenize(f"{ticket_dict.get('titre') or ''} {ticket_dict.get('description') or ''}")
            for history_ticket in history_items:
                history_ticket_dict = dict(history_ticket)
                history_text = _tokenize(f"{history_ticket_dict.get('titre') or ''} {history_ticket_dict.get('description') or ''}")
                overlap = len(ticket_text & history_text)
                if overlap > 0:
                    score += overlap * 2
                    evidence.append({
                        "history_ticket_id": history_ticket_dict.get("id"),
                        "titre": history_ticket_dict.get("titre"),
                        "overlap": overlap,
                    })
                if history_ticket_dict.get("categorie") == ticket_dict.get("categorie"):
                    score += 4
                if history_ticket_dict.get("departement_cible") == ticket_dict.get("departement_cible"):
                    score += 2
                if history_ticket_dict.get("statut") in {"en_cours", "resolu", "traité", "traitée"}:
                    score += 1
        if score > 0:
            scored_users.append((score, user, evidence[:3]))

    if not scored_users:
        recommended_user = users[0] if users else None
        evidence = []
    else:
        scored_users.sort(key=lambda item: item[0], reverse=True)
        best_score, recommended_user, evidence = scored_users[0]

    if recommended_user is None:
        return {"group_id": group_id, "group_title": group_row["titre_probleme"], "recommended_user": None, "reason": "Aucun historique de ticket similaire n’a pu être trouvé.", "history_matches": []}

    return {
        "group_id": group_id,
        "group_title": group_row["titre_probleme"],
        "recommended_user": {
            "id": recommended_user["id"],
            "nom": recommended_user["nom"],
            "email": recommended_user["email"],
            "departement": recommended_user["departement"],
        },
        "reason": "Suggestion IA fondée sur l’historique des tickets similaires et les anciens tickets déjà traités dans le même domaine.",
        "history_matches": evidence,
        "score": best_score if scored_users else 0,
    }


def group_problem_tickets():
    """Regroupe les tickets par thématique de problème à partir des groupes de problèmes existants."""
    conn = get_db()
    groups = conn.execute(
        "SELECT id, titre_probleme, statut, ticket_maitre_id FROM probleme_groupes ORDER BY id"
    ).fetchall()

    grouped = []
    for group in groups:
        tickets = conn.execute(
            "SELECT id, titre, categorie, statut, departement_cible FROM tickets WHERE groupe_id = ? ORDER BY id DESC",
            (group["id"],),
        ).fetchall()
        categories = {}
        for ticket in tickets:
            categories[ticket["categorie"]] = categories.get(ticket["categorie"], 0) + 1
        grouped.append({
            "group_id": group["id"],
            "titre": group["titre_probleme"],
            "statut": group["statut"],
            "ticket_maitre_id": group["ticket_maitre_id"],
            "ticket_count": len(tickets),
            "categories": categories,
            "tickets": [dict(row) for row in tickets],
        })
    conn.close()

    return {
        "message": "problem groups prepared",
        "groups": grouped,
        "summary": {
            "total_groups": len(grouped),
            "total_tickets": sum(group["ticket_count"] for group in grouped),
        },
    }


def get_problem_updates(problem_group_id=None):
    """Retourne un flux de mise à jour de groupe de problème, à utiliser par le frontend pour afficher l’état du groupe."""
    conn = get_db()
    if problem_group_id is None:
        rows = conn.execute(
            "SELECT id, titre_probleme, statut FROM probleme_groupes ORDER BY id"
        ).fetchall()
        groups = []
        for row in rows:
            groups.append({
                "group_id": row["id"],
                "titre": row["titre_probleme"],
                "statut": row["statut"],
            })
        conn.close()
        return {"message": "problem updates ready", "groups": groups}

    group_row = conn.execute(
        "SELECT id, titre_probleme, statut FROM probleme_groupes WHERE id = ?",
        (problem_group_id,),
    ).fetchone()
    rows = conn.execute(
        "SELECT id, titre, statut, departement_cible FROM tickets WHERE groupe_id = ? ORDER BY id DESC",
        (problem_group_id,),
    ).fetchall()
    conn.close()
    return {
        "message": "group updates ready",
        "group_id": problem_group_id,
        "group_title": group_row["titre_probleme"] if group_row else "Groupe inconnu",
        "group_status": group_row["statut"] if group_row else "inconnu",
        "tickets": [dict(r) for r in rows],
    }
