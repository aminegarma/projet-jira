import json
import re

import requests

from config import Config


SEVERITY_ALIASES = {
    "low": "faible",
    "faible": "faible",
    "medium": "moyenne",
    "moyen": "moyenne",
    "moyenne": "moyenne",
    "high": "haute",
    "haut": "haute",
    "haute": "haute",
    "critical": "critique",
    "critique": "critique",
}

PRIORITY_ALIASES = {
    "low": "faible",
    "faible": "faible",
    "medium": "normal",
    "moyen": "normal",
    "moyenne": "normal",
    "normal": "normal",
    "normale": "normal",
    "high": "urgent",
    "haut": "urgent",
    "haute": "urgent",
    "urgent": "urgent",
    "urgente": "urgent",
    "critical": "urgent",
    "critique": "urgent",
}


def _clean_model_json(content):
    text = str(content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _normalize_model_result(parsed):
    if not isinstance(parsed, dict):
        return None

    severity_raw = str(parsed.get("gravite") or parsed.get("severity") or "moyenne").strip().lower()
    priority_raw = str(parsed.get("priorite") or parsed.get("priority") or "normal").strip().lower()
    department = str(parsed.get("departement") or parsed.get("department") or "Support").strip()
    category = str(parsed.get("categorie") or parsed.get("category") or "support").strip()

    return {
        "categorie": category or "support",
        "gravite": SEVERITY_ALIASES.get(severity_raw, "moyenne"),
        "priorite": PRIORITY_ALIASES.get(priority_raw, "normal"),
        "departement": department or "Support",
        "source": "mistral",
    }


def _heuristic_classification(description):
    lower = (description or "").lower()

    if any(word in lower for word in ["connexion", "sso", "login", "auth", "mot de passe", "session", "token", "acces", "access", "se connecter", "connexion bloquée", "connecter", "connecte", "connecté"]):
        categorie = "access"
        departement = "IT"
    elif any(word in lower for word in ["facture", "paiement", "finance", "bulletin", "salaire", "compta"]):
        categorie = "facturation"
        departement = "Finance"
    elif any(word in lower for word in ["rh", "contrat", "ressource humaine", "recrutement", "paie"]):
        categorie = "rh"
        departement = "RH"
    elif any(word in lower for word in ["achat", "commande", "livraison", "fournisseur", "stock"]):
        categorie = "achats"
        departement = "Achats"
    elif any(word in lower for word in ["bug", "erreur", "incident", "plantage", "affichage", "rapport", "interface"]):
        categorie = "bug"
        departement = "Produit"
    else:
        categorie = "autre"
        departement = "Support"

    if any(word in lower for word in ["bloquant", "critique", "outage", "impossible", "ne plus"]):
        gravite = "haute"
    elif any(word in lower for word in ["urgent", "important", "prioritaire"]):
        gravite = "moyenne"
    else:
        gravite = "faible"

    if gravite == "haute":
        priorite = "urgent"
    elif gravite == "moyenne":
        priorite = "normal"
    else:
        priorite = "faible"

    return {
        "categorie": categorie,
        "gravite": gravite,
        "priorite": priorite,
        "departement": departement,
        "source": "heuristic",
    }


def classify_ticket(description):
    """Classifie un ticket avec Mistral, puis utilise une logique locale en cas d'échec."""
    api_key = Config.MISTRAL_API_KEY
    if api_key and api_key != "à_remplacer":
        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistral-small-latest",
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Tu classifies des tickets support. Réponds uniquement en JSON avec "
                                "categorie, gravite, priorite et departement. "
                                "gravite doit être faible, moyenne, haute ou critique. "
                                "priorite doit être faible, normal ou urgent."
                            ),
                        },
                        {"role": "user", "content": description or ""},
                    ],
                },
                timeout=10,
            )
            if response.ok:
                payload = response.json()
                content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    parsed = json.loads(_clean_model_json(content))
                    normalized = _normalize_model_result(parsed)
                    if normalized:
                        return normalized
        except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
            pass

    return _heuristic_classification(description)
