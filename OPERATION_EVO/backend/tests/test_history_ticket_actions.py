import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import controllers.ticket_controller as ticket_controller
import database.db as db_module


class HistoryTicketActionsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test_app.db")
        schema_path = Path(__file__).resolve().parents[1] / "database" / "init_db.sql"
        with open(schema_path, "r", encoding="utf-8") as handle:
            schema_sql = handle.read()
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()

        self.db_patcher = patch.object(db_module, "DB_PATH", self.db_path)
        self.db_patcher.start()
        self.addCleanup(self.db_patcher.stop)
        self.addCleanup(self.tmpdir.cleanup)

    def test_get_history_tickets_returns_history_rows(self):
        rows = ticket_controller.get_history_tickets()

        self.assertTrue(isinstance(rows, list))
        self.assertGreaterEqual(len(rows), 1)
        self.assertTrue(any(ticket.get("statut") in {"resolu", "résolu", "traité", "traitée", "reçu", "recu"} for ticket in rows))

    def test_delete_ticket_removes_the_ticket(self):
        deleted = ticket_controller.delete_ticket(1)

        self.assertEqual(deleted["id"], 1)
        self.assertIsNone(ticket_controller.get_ticket_by_id(1))


if __name__ == "__main__":
    unittest.main()
