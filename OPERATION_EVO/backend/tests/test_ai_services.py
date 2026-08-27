import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import database.db as db_module
from config import Config
from services.mistral_service import classify_ticket
from services.similarity_service import (
    build_ai_suggestions,
    get_problem_updates,
    group_problem_tickets,
    suggest_group_assignment,
)


class AiServicesTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "ai_services.db")
        self.db_patcher = patch.object(db_module, "DB_PATH", self.db_path)
        self.db_patcher.start()
        db_module.init_db(force=True)
        self.addCleanup(self.db_patcher.stop)
        self.addCleanup(self.tmpdir.cleanup)

    def test_classification_and_suggestions(self):
        ticket_text = "Je ne peux plus me connecter au portail via SSO"
        classification = classify_ticket(ticket_text)
        suggestions = build_ai_suggestions(ticket_text)

        self.assertEqual(classification["categorie"], "access")
        self.assertIn("classification", suggestions)
        self.assertTrue(suggestions["similar_tickets"])
        self.assertTrue(suggestions["suggested_users"])


    def test_mistral_response_is_normalized_to_backend_values(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "```json\n{\"categorie\": \"Incident IT\", \"gravite\": \"Haute\", \"priorite\": \"Haute\", \"departement\": \"DSI\"}\n```"
                }
            }]
        }
        with patch.object(Config, "MISTRAL_API_KEY", "demo-key"), patch(
            "services.mistral_service.requests.post", return_value=response
        ):
            result = classify_ticket("Incident de connexion critique")

        self.assertEqual(result["gravite"], "haute")
        self.assertEqual(result["priorite"], "urgent")
        self.assertEqual(result["source"], "mistral")

    def test_suggestions_reason_mentions_history(self):
        suggestions = build_ai_suggestions("Problème de connexion au portail SSO")
        reason = suggestions.get("reason", "").lower()
        self.assertTrue(
            "historique" in reason or "similaire" in reason or "historiques" in reason,
            msg=f"Reason was expected to mention historical evidence, got: {suggestions.get('reason')}"
        )

    def test_suggest_group_assignment_returns_json_safe_payload(self):
        suggestion = suggest_group_assignment(1)
        self.assertEqual(suggestion[1], 404) if isinstance(suggestion, tuple) else None
        self.assertIn("recommended_user", suggestion)
        self.assertIn("reason", suggestion)
        self.assertIn("history_matches", suggestion)


if __name__ == "__main__":
    unittest.main()
