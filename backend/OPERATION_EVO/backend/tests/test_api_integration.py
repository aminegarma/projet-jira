import importlib
import os
import tempfile
import unittest
from pathlib import Path

try:
    import flask  # noqa: F401
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask dependencies are not installed in this execution environment")
class ApiIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.db_path = str(Path(cls.tmpdir.name) / "api_integration.db")

        os.environ["FLASK_ENV"] = "test"
        os.environ["DISABLE_EMAIL_WORKER"] = "true"

        import database.db as db_module

        cls.db_module = db_module
        cls.original_db_path = db_module.DB_PATH
        db_module.DB_PATH = cls.db_path
        db_module.init_db(force=True)

        app_module = importlib.import_module("app")
        app_module.app.config.update(TESTING=True)
        cls.app = app_module.app

    @classmethod
    def tearDownClass(cls):
        cls.db_module.DB_PATH = cls.original_db_path
        cls.tmpdir.cleanup()

    def setUp(self):
        self.db_module.init_db(force=True)
        self.client = self.app.test_client()

    def login_admin(self):
        return self.client.post(
            "/login",
            data={"email": "admin@operation-evo.local", "password": "Admin123!"},
            follow_redirects=False,
        )

    def test_authentication_and_crud_workflow(self):
        protected = self.client.get("/admin")
        self.assertEqual(protected.status_code, 302)
        self.assertIn("/login", protected.headers["Location"])

        login = self.login_admin()
        self.assertEqual(login.status_code, 302)
        self.assertIn("/admin", login.headers["Location"])
        self.assertEqual(self.client.get("/admin").status_code, 200)

        created_user = self.client.post(
            "/api/users",
            json={
                "nom": "Agent API",
                "email": "agent.api@example.com",
                "departement": "IT",
                "role": "user",
                "password": "Demo123!",
            },
        )
        self.assertEqual(created_user.status_code, 201)
        user_id = created_user.get_json()["id"]

        created_ticket = self.client.post(
            "/api/tickets",
            json={
                "titre": "Incident API de démonstration",
                "description": "Connexion SSO impossible pour plusieurs utilisateurs",
                "user_id": user_id,
            },
        )
        self.assertEqual(created_ticket.status_code, 201)
        ticket_id = created_ticket.get_json()["id"]

        updated_ticket = self.client.put(
            f"/api/tickets/{ticket_id}",
            json={"statut": "en_cours", "priorite": "urgent"},
        )
        self.assertEqual(updated_ticket.status_code, 200)
        self.assertEqual(updated_ticket.get_json()["ticket"]["statut"], "en_cours")

        comment = self.client.post(
            f"/api/tickets/{ticket_id}/comments",
            json={"message": "Prise en charge par le support."},
        )
        self.assertEqual(comment.status_code, 201)
        self.assertEqual(len(self.client.get(f"/api/tickets/{ticket_id}/comments").get_json()), 1)

        group = self.client.post(
            "/api/tickets/problem-groups",
            json={"titre_probleme": "Incident API groupé", "ticket_maitre_id": ticket_id},
        )
        self.assertEqual(group.status_code, 201)
        group_id = group.get_json()["group"]["id"]
        suggestion = self.client.get(
            f"/api/tickets/problem-groups/{group_id}/suggest-assignee"
        )
        self.assertEqual(suggestion.status_code, 200)
        self.assertIn("recommended_user", suggestion.get_json())

        self.assertEqual(self.client.delete(f"/api/tickets/{ticket_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/users/{user_id}").status_code, 200)

        logout = self.client.post("/logout", json={})
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/api/tickets").status_code, 401)

    def test_agent_uses_separate_dashboard_and_scoped_api(self):
        login = self.client.post(
            "/login",
            data={"email": "agent@operation-evo.local", "password": "Agent123!"},
            follow_redirects=False,
        )
        self.assertEqual(login.status_code, 302)
        self.assertIn("/dashboard", login.headers["Location"])
        self.assertEqual(self.client.get("/dashboard").status_code, 200)

        admin_page = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(admin_page.status_code, 302)
        self.assertIn("/dashboard", admin_page.headers["Location"])

        me = self.client.get("/api/auth/me").get_json()
        self.assertEqual(me["role"], "user")

        denied = self.client.post(
            "/api/users",
            json={"nom": "Interdit", "email": "forbidden@example.com"},
        )
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.client.get("/api/users").status_code, 403)
        self.assertEqual(self.client.get("/api/tickets/problem-groups").status_code, 403)

        own_ticket = self.client.post(
            "/api/tickets",
            json={
                "titre": "Demande créée par un utilisateur",
                "description": "Le portail ne répond pas correctement.",
                "user_id": 1,
                "statut": "resolu",
            },
        )
        self.assertEqual(own_ticket.status_code, 201)
        created = own_ticket.get_json()["ticket"]
        self.assertEqual(created["user_id"], me["id"])
        self.assertEqual(created["statut"], "ouvert")

        visible = self.client.get("/api/tickets").get_json()
        self.assertTrue(visible)
        self.assertTrue(all(int(ticket["user_id"]) == int(me["id"]) for ticket in visible))

        conn = self.db_module.get_db()
        foreign_ticket = conn.execute(
            "SELECT id FROM tickets WHERE user_id != ? AND user_id IS NOT NULL LIMIT 1",
            (me["id"],),
        ).fetchone()
        conn.close()
        self.assertIsNotNone(foreign_ticket)
        self.assertEqual(self.client.get(f"/api/tickets/{foreign_ticket['id']}").status_code, 403)
        self.assertEqual(
            self.client.post(f"/api/tickets/{created['id']}/assign", json={"user_id": 2}).status_code,
            403,
        )


if __name__ == "__main__":
    unittest.main()
