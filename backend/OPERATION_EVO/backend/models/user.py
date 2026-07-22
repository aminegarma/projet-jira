from flask_login import UserMixin


class User(UserMixin):
    def __init__(
        self,
        id=None,
        nom=None,
        email=None,
        poste=None,
        departement=None,
        role="user",
        active=True,
    ):
        self.id = int(id) if id is not None else None
        self.nom = nom
        self.email = email
        self.poste = poste
        self.departement = departement
        self.role = role or "user"
        self.active = bool(active)

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.role == "admin"

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        keys = set(row.keys())
        return cls(
            id=row["id"],
            nom=row["nom"],
            email=row["email"],
            poste=row["poste"] if "poste" in keys else None,
            departement=row["departement"] if "departement" in keys else None,
            role=row["role"] if "role" in keys else "user",
            active=row["active"] if "active" in keys else 1,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "poste": self.poste,
            "departement": self.departement,
            "role": self.role,
            "active": self.active,
        }
