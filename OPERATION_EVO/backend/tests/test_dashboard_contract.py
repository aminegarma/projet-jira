import re
import unittest
from pathlib import Path


class DashboardContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = (
            Path(__file__).resolve().parents[1] / "templates" / "admin_dashboard.html"
        ).read_text(encoding="utf-8")

    def test_mandatory_crud_controls_are_present(self):
        for element_id in (
            "new_ticket_btn",
            "ticket_form",
            "new_user_btn",
            "user_form",
            "new_group_btn",
            "group_form",
            "logout_btn",
        ):
            self.assertIn(f'id="{element_id}"', self.template)

    def test_dashboard_uses_real_ai_suggestion_endpoint(self):
        self.assertIn(
            "/api/tickets/problem-groups/${group.group_id}/suggest-assignee",
            self.template,
        )
        self.assertNotIn("fallbackUser", self.template)
        self.assertNotRegex(self.template, re.compile(r"find\([^\n]*id\)\s*===\s*2"))

    def test_history_pin_is_not_exposed(self):
        lowered = self.template.lower()
        self.assertNotIn("historypin", lowered)
        self.assertNotIn("pin habilitant", lowered)

    def test_api_response_and_html_escaping_helpers_exist(self):
        self.assertIn("async function api", self.template)
        self.assertIn("const esc = value", self.template)
        self.assertIn("response.status===401", self.template)


if __name__ == "__main__":
    unittest.main()
