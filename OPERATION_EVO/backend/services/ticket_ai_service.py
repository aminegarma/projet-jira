import hashlib
import math
import time
from typing import Any, Dict, List, Optional

from database.db import get_db
from services.mistral_service import classify_ticket
from services.similarity_service import build_ai_suggestions

_CACHE_TTL_SECONDS = 600
_ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}


def _estimate_tokens(text: str) -> int:
    # Rough estimate commonly used for Latin scripts.
    return max(1, math.ceil(len(text or "") / 4))


def _clip(value: Optional[str], limit: int) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _compact_lines(items: List[str], max_chars: int) -> str:
    out: List[str] = []
    consumed = 0
    for item in items:
        entry = str(item or "").strip()
        if not entry:
            continue
        if consumed + len(entry) + 1 > max_chars:
            break
        out.append(entry)
        consumed += len(entry) + 1
    return "\n".join(out)


def _build_cache_key(ticket: Dict[str, Any], comments: List[Dict[str, Any]], activity: List[Dict[str, Any]], entity: str) -> str:
    fingerprint = {
        "ticket_id": ticket.get("id"),
        "status": ticket.get("statut"),
        "priority": ticket.get("priorite"),
        "entity": entity,
        "ticket_title": ticket.get("titre"),
        "ticket_desc": ticket.get("description"),
        "last_comment_id": comments[-1].get("id") if comments else None,
        "comment_count": len(comments),
        "last_activity_id": activity[-1].get("id") if activity else None,
        "activity_count": len(activity),
    }
    digest = hashlib.sha256(str(fingerprint).encode("utf-8")).hexdigest()
    return digest


def _cleanup_cache() -> None:
    now = time.time()
    stale_keys = [key for key, item in _ANALYSIS_CACHE.items() if now - item["created_at"] > _CACHE_TTL_SECONDS]
    for key in stale_keys:
        _ANALYSIS_CACHE.pop(key, None)


def _build_recommendations(ticket: Dict[str, Any], classification: Dict[str, Any], similar_tickets: List[Dict[str, Any]]) -> List[str]:
    status = str(ticket.get("statut") or "").lower()
    priority = str(ticket.get("priorite") or "").lower()
    department = classification.get("departement") or ticket.get("departement_cible") or "Support"

    actions: List[str] = []
    if priority == "urgent" and status != "resolu":
        actions.append("Escalader immédiatement au responsable du domaine et ouvrir un suivi prioritaire.")
    if status == "ouvert":
        actions.append("Qualifier le ticket puis affecter un agent spécialiste du département concerné.")
    if status == "en_cours":
        actions.append("Demander un point d'avancement et bloquer la prochaine mise à jour dans moins de 24h.")
    if status == "resolu":
        actions.append("Valider la résolution avec le demandeur et documenter la solution dans la base de connaissances.")

    if similar_tickets:
        top = similar_tickets[0]
        actions.append(
            f"Réutiliser la stratégie du ticket similaire #{top.get('id')} ({top.get('titre')}) pour accélérer la résolution."
        )

    actions.append(f"Vérifier les impacts transverses sur l'entité {department} avant clôture.")
    return actions[:5]


def analyze_ticket_problem_solving(ticket_id: int, *, entity: Optional[str] = None, max_comments: int = 6, max_activity: int = 8) -> Dict[str, Any]:
    conn = get_db()
    ticket_row = conn.execute(
        """
        SELECT t.id, t.titre, t.description, t.categorie, t.gravite, t.priorite,
               t.departement_cible, t.statut, t.date_creation, t.user_id,
               u.nom AS user_nom, u.email AS user_email
        FROM tickets t
        LEFT JOIN users u ON u.id = t.user_id
        WHERE t.id = ?
        """,
        (ticket_id,),
    ).fetchone()

    if ticket_row is None:
        conn.close()
        return {"error": "ticket not found"}

    comments_rows = conn.execute(
        """
        SELECT c.id, c.message, c.date_creation, u.nom AS user_name
        FROM ticket_comments c
        LEFT JOIN users u ON u.id = c.user_id
        WHERE c.ticket_id = ?
        ORDER BY c.id DESC
        LIMIT ?
        """,
        (ticket_id, max_comments),
    ).fetchall()

    activity_rows = conn.execute(
        """
        SELECT id, action, created_at
        FROM ticket_activity
        WHERE ticket_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (ticket_id, max_activity),
    ).fetchall()
    conn.close()

    ticket = dict(ticket_row)
    comments = [dict(row) for row in reversed(comments_rows)]
    activity = [dict(row) for row in reversed(activity_rows)]
    analysis_entity = (entity or ticket.get("departement_cible") or ticket.get("categorie") or "Support").strip()

    cache_key = _build_cache_key(ticket, comments, activity, analysis_entity)
    _cleanup_cache()
    cached = _ANALYSIS_CACHE.get(cache_key)
    if cached:
        result = dict(cached["result"])
        result["cache"] = {"hit": True, "ttl_seconds": _CACHE_TTL_SECONDS}
        return result

    comments_lines = [
        f"- {item.get('user_name') or 'Système'}: {_clip(item.get('message'), 220)}"
        for item in comments
    ]
    activity_lines = [
        f"- {item.get('action')} ({item.get('created_at')})"
        for item in activity
    ]

    raw_context = (
        f"Ticket #{ticket.get('id')}\n"
        f"Titre: {ticket.get('titre')}\n"
        f"Description: {ticket.get('description')}\n"
        f"Entité: {analysis_entity}\n"
        f"Commentaires:\n" + "\n".join(comments_lines) + "\n"
        f"Activité:\n" + "\n".join(activity_lines)
    )

    compact_comments = _compact_lines(comments_lines, max_chars=900)
    compact_activity = _compact_lines(activity_lines, max_chars=600)
    reduced_context = (
        f"Ticket #{ticket.get('id')} | Entité: {analysis_entity}\n"
        f"Titre: {_clip(ticket.get('titre'), 180)}\n"
        f"Détail: {_clip(ticket.get('description'), 650)}\n"
        f"Commentaires clés:\n{compact_comments or '- Aucun commentaire'}\n"
        f"Activité clé:\n{compact_activity or '- Aucune activité'}"
    )

    classification = classify_ticket(f"{ticket.get('titre') or ''}\n{ticket.get('description') or ''}\n{compact_comments}")
    suggestions = build_ai_suggestions(
        {
            "titre": ticket.get("titre"),
            "description": f"{ticket.get('description') or ''}\n{compact_comments}",
            "categorie": ticket.get("categorie"),
            "departement_cible": ticket.get("departement_cible"),
        }
    )

    similar_tickets = suggestions.get("similar_tickets") or []
    recommendations = _build_recommendations(ticket, classification, similar_tickets)

    result = {
        "ticket_number": ticket.get("id"),
        "entity": analysis_entity,
        "detail": _clip(ticket.get("description"), 900),
        "jira_ia": {
            "ticket_number": ticket.get("id"),
            "entity": analysis_entity,
            "comment_count": len(comments),
            "comments": comments,
            "activity": activity,
            "classification": classification,
            "similar_tickets": similar_tickets[:3],
            "problem_summary": f"{ticket.get('titre')} - {classification.get('departement', analysis_entity)}",
            "proposed_actions": recommendations,
        },
        "token_optimization": {
            "context_before_chars": len(raw_context),
            "context_after_chars": len(reduced_context),
            "estimated_tokens_before": _estimate_tokens(raw_context),
            "estimated_tokens_after": _estimate_tokens(reduced_context),
            "reduction_percent": round(
                (1 - (_estimate_tokens(reduced_context) / max(1, _estimate_tokens(raw_context)))) * 100,
                1,
            ),
        },
        "context_preview": reduced_context,
        "cache": {"hit": False, "ttl_seconds": _CACHE_TTL_SECONDS},
    }

    _ANALYSIS_CACHE[cache_key] = {"created_at": time.time(), "result": result}
    return result
