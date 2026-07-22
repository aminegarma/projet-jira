import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import database.db as db_module


class DatabaseInitializationTestCase(unittest.TestCase):
    def test_init_db_preserves_existing_data_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_app.db")
            schema_path = Path(__file__).resolve().parents[1] / "database" / "init_db.sql"

            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE custom_table (id INTEGER PRIMARY KEY, value TEXT)")
            conn.execute("INSERT INTO custom_table (value) VALUES ('keep-me')")
            conn.commit()
            conn.close()

            with patch.object(db_module, "DB_PATH", db_path), patch.object(db_module, "SCHEMA_PATH", schema_path):
                result = db_module.init_db(force=False)

            self.assertEqual(result, db_path)
            conn = sqlite3.connect(db_path)
            row = conn.execute("SELECT value FROM custom_table WHERE value = 'keep-me'").fetchone()
            conn.close()
            self.assertIsNotNone(row)


if __name__ == "__main__":
    unittest.main()
