import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import database.db as db_module
from controllers.auth_controller import authenticate_user
from controllers.problem_group_controller import (
    create_problem_group,
    delete_problem_group,
    update_problem_group,
)
from controllers.ticket_controller import create_ticket, delete_ticket, get_ticket_by_id, update_ticket
from controllers.user_controller import create_user, delete_user, get_user_by_id, update_user


class MandatoryFeaturesTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "operation_evo_test.db")
        self.db_patcher = patch.object(db_module, "DB_PATH", self.db_path)
        self.db_patcher.start()
        db_module.init_db(force=True)
        self.addCleanup(self.db_patcher.stop)
        self.addCleanup(self.tmpdir.cleanup)

    def test_demo_admin_authentication(self):
        admin = authenticate_user("admin@operation-evo.local", "Admin123!")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.role, "admin")
        self.assertIsNone(authenticate_user("admin@operation-evo.local", "wrong-password"))

    def test_user_crud(self):
        created = create_user({
            "nom": "Utilisateur Test",
            "email": "user.test@example.com",
            "departement": "IT",
            "role": "user",
            "password": "Demo123!",
        })
        self.assertNotIsInstance(created, tuple)
        user_id = created["id"]
        self.assertEqual(get_user_by_id(user_id)["email"], "user.test@example.com")

        updated = update_user(user_id, {"role": "manager", "departement": "Produit"})
        self.assertEqual(updated["user"]["role"], "manager")
        self.assertEqual(updated["user"]["departement"], "Produit")

        deleted = delete_user(user_id)
        self.assertEqual(deleted["id"], user_id)
        self.assertIsNone(get_user_by_id(user_id))

    def test_ticket_crud(self):
        created = create_ticket({
            "titre": "Erreur de connexion de démonstration",
            "description": "Impossible de se connecter au portail SSO",
            "statut": "ouvert",
        })
        self.assertNotIsInstance(created, tuple)
        ticket_id = created["id"]
        self.assertEqual(get_ticket_by_id(ticket_id)["categorie"], "access")

        updated = update_ticket(ticket_id, {
            "titre": "Erreur SSO corrigée",
            "statut": "resolu",
            "priorite": "normal",
            "user_id": 2,
        })
        self.assertEqual(updated["ticket"]["titre"], "Erreur SSO corrigée")
        self.assertEqual(updated["ticket"]["statut"], "resolu")

        deleted = delete_ticket(ticket_id)
        self.assertEqual(deleted["id"], ticket_id)
        self.assertIsNone(get_ticket_by_id(ticket_id))

    def test_problem_group_crud(self):
        created = create_problem_group({"titre_probleme": "Groupe test", "statut": "ouvert"})
        self.assertNotIsInstance(created, tuple)
        group_id = created["group"]["id"]

        updated = update_problem_group(group_id, {"titre_probleme": "Groupe modifié", "statut": "en_cours"})
        self.assertEqual(updated["group"]["titre_probleme"], "Groupe modifié")
        self.assertEqual(updated["group"]["statut"], "en_cours")

        deleted = delete_problem_group(group_id)
        self.assertEqual(deleted["id"], group_id)


if __name__ == "__main__":
    unittest.main()
