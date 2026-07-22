import unittest
from pathlib import Path


class UserDashboardContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = (
            Path(__file__).resolve().parents[1] / "templates" / "user_dashboard.html"
        ).read_text(encoding="utf-8")
        cls.app_source = (
            Path(__file__).resolve().parents[1] / "app.py"
        ).read_text(encoding="utf-8")
        cls.auth_source = (
            Path(__file__).resolve().parents[1] / "routes" / "auth.py"
        ).read_text(encoding="utf-8")
        cls.ticket_routes = (
            Path(__file__).resolve().parents[1] / "routes" / "tickets.py"
        ).read_text(encoding="utf-8")

    def test_separate_user_dashboard_exists(self):
        self.assertIn('@app.route("/dashboard"', self.app_source)
        self.assertIn('render_template("user_dashboard.html"', self.app_source)
        self.assertIn("Espace utilisateur", self.template)
        self.assertIn('id="new_ticket_btn"', self.template)
        self.assertIn('id="tickets_table"', self.template)

    def test_login_redirect_is_role_aware(self):
        self.assertIn('"admin_dashboard" if user.role == "admin" else "user_dashboard"', self.auth_source)

    def test_regular_ticket_list_is_server_scoped(self):
        self.assertIn('filters["user_id"] = current_user.id', self.ticket_routes)
        self.assertIn('allowed_user_fields = {"titre", "description", "statut"}', self.ticket_routes)
        self.assertIn('@admin_required\ndef assign_ticket_route', self.ticket_routes)

    def test_user_dashboard_does_not_load_admin_resources(self):
        self.assertNotIn('/api/users', self.template)
        self.assertNotIn('/api/tickets/problem-groups', self.template)
        self.assertNotIn('/api/tickets/metrics', self.template)


if __name__ == "__main__":
    unittest.main()
