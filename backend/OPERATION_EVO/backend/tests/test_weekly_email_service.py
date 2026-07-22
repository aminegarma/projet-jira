import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import database.db as db_module
from services.email_service import build_weekly_system_summary


class WeeklyEmailServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "weekly_email.db")
        self.db_patcher = patch.object(db_module, "DB_PATH", self.db_path)
        self.db_patcher.start()
        db_module.init_db(force=True)
        self.addCleanup(self.db_patcher.stop)
        self.addCleanup(self.tmpdir.cleanup)

    def test_build_weekly_system_summary_contains_summary_sections(self):
        summary = build_weekly_system_summary()
        self.assertIn('Résumé hebdomadaire', summary)
        self.assertIn('Tickets', summary)
        self.assertIn('Évolution', summary)


if __name__ == '__main__':
    unittest.main()
