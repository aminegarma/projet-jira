import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from database.db import get_db
from config import Config


DEFAULT_RECIPIENT = os.getenv('SYSTEM_EMAIL_RECIPIENT', Config.SYSTEM_EMAIL_RECIPIENT)


def _build_smtp_connection():
    host = os.getenv('SMTP_HOST', Config.SMTP_HOST)
    port = int(os.getenv('SMTP_PORT', str(Config.SMTP_PORT)))
    username = os.getenv('SMTP_USERNAME', Config.SMTP_USERNAME)
    password = os.getenv('SMTP_PASSWORD', Config.SMTP_PASSWORD)
    use_tls = os.getenv('SMTP_USE_TLS', str(Config.SMTP_USE_TLS)).lower() == 'true'

    server = smtplib.SMTP(host, port)
    if use_tls:
        server.starttls()
    if username and password:
        server.login(username, password)
    return server


def _get_stats_snapshot():
    conn = get_db()
    stats = {
        'total_tickets': conn.execute("SELECT COUNT(*) as count FROM tickets").fetchone()['count'],
        'tickets_ouverts': conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'ouvert'").fetchone()['count'],
        'tickets_en_cours': conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'en_cours'").fetchone()['count'],
        'tickets_resolus': conn.execute("SELECT COUNT(*) as count FROM tickets WHERE statut = 'resolu'").fetchone()['count'],
    }
    conn.close()
    return stats


def build_weekly_system_summary():
    stats = _get_stats_snapshot()
    summary = [
        'Résumé hebdomadaire',
        '',
        'Tickets',
        f"- Total : {stats['total_tickets']}",
        f"- Ouverts : {stats['tickets_ouverts']}",
        f"- En cours : {stats['tickets_en_cours']}",
        f"- Résolus : {stats['tickets_resolus']}",
        '',
        'Évolution',
        '- Le système continue de suivre un volume stable de tickets à traiter.',
        '- Les groupes ayant le plus de tickets doivent être priorisés cette semaine.',
    ]
    return '\n'.join(summary)


def send_weekly_system_email(recipient=None, subject='Résumé hebdomadaire du système'):
    recipient = recipient or DEFAULT_RECIPIENT
    body = build_weekly_system_summary()

    if not os.getenv('SMTP_HOST') and not Config.SMTP_USERNAME:
        return {
            'status': 'simulated',
            'recipient': recipient,
            'subject': subject,
            'body': body,
        }

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = os.getenv('SMTP_FROM', Config.SMTP_FROM or 'noreply@outlook.com')
        msg['To'] = recipient
        msg.set_content(body)

        with _build_smtp_connection() as server:
            server.send_message(msg)
        return {'status': 'sent', 'recipient': recipient, 'subject': subject}
    except Exception as exc:
        return {'status': 'error', 'recipient': recipient, 'error': str(exc)}


def send_ticket_notification(ticket_id, event_name, recipient=None):
    """Envoie une notification simulée pour un événement lié à un ticket."""
    conn = get_db()
    ticket = conn.execute(
        "SELECT id, titre, statut, user_id FROM tickets WHERE id = ?",
        (ticket_id,),
    ).fetchone()
    conn.close()
    if ticket is None:
        return {"status": "error", "error": "ticket not found"}
    body = f"Ticket #{ticket_id} - {event_name} - {ticket['titre']}"
    return {
        "status": "simulated",
        "recipient": recipient or DEFAULT_RECIPIENT,
        "event": event_name,
        "ticket_id": ticket_id,
        "body": body,
    }
