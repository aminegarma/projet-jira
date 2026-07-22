import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from controllers.ticket_controller import (
    create_ticket,
    create_ticket_comment,
    export_tickets,
    get_ticket_activity,
    get_ticket_comments,
    get_ticket_metrics_summary,
    update_ticket_status,
)
import database.db as db_module


class BackendPhasesTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "backend_phases.db")
        self.db_patcher = patch.object(db_module, "DB_PATH", self.db_path)
        self.db_patcher.start()
        db_module.init_db(force=True)
        self.addCleanup(self.db_patcher.stop)
        self.addCleanup(self.tmpdir.cleanup)

    def test_status_update_creates_activity_and_comment(self):
        created = create_ticket({
            "titre": "Problème de connexion",
            "description": "Je ne peux pas me connecter",
            "user_id": 1,
        })
        updated = update_ticket_status(
            created["id"],
            new_status="en_cours",
            assigned_user_id=2,
            priority="urgent",
            metadata={"source": "backend-test"},
        )
        comment = create_ticket_comment(created["id"], user_id=1, text="Analyse en cours")
        activity = get_ticket_activity(created["id"])

        self.assertEqual(updated["statut"], "en_cours")
        self.assertEqual(comment["ticket_id"], created["id"])
        self.assertEqual(comment["message"], "Analyse en cours")
        self.assertTrue(any(item["action"] == "status_changed" for item in activity))
        self.assertTrue(any(item["action"] == "assigned" for item in activity))
        self.assertTrue(any(item["action"] == "comment_added" for item in activity))
        self.assertEqual(len(get_ticket_comments(created["id"])), 1)

    def test_export_tickets_supports_csv(self):
        create_ticket({
            "titre": "Erreur d’impression",
            "description": "L’impression échoue",
            "user_id": 1,
        })
        exported = export_tickets(format="csv")
        self.assertIn("id,titre,statut", exported)
        self.assertIn("Erreur d’impression", exported)

    def test_metrics_summary_contains_counts_by_status(self):
        create_ticket({
            "titre": "Problème de connexion",
            "description": "Je ne peux pas me connecter",
            "user_id": 1,
        })
        summary = get_ticket_metrics_summary()
        self.assertGreater(summary["total_tickets"], 0)
        self.assertIn("by_status", summary)
        self.assertIn("by_priority", summary)


if __name__ == "__main__":
    unittest.main()
