class Ticket:
    def __init__(self, id=None, titre=None, description=None, categorie=None, gravite=None, priorite=None,
                 departement_cible=None, statut=None, date_creation=None, user_id=None, groupe_id=None):
        self.id = id
        self.titre = titre
        self.description = description
        self.categorie = categorie
        self.gravite = gravite
        self.priorite = priorite
        self.departement_cible = departement_cible
        self.statut = statut
        self.date_creation = date_creation
        self.user_id = user_id
        self.groupe_id = groupe_id

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "categorie": self.categorie,
            "gravite": self.gravite,
            "priorite": self.priorite,
            "departement_cible": self.departement_cible,
            "statut": self.statut,
            "date_creation": self.date_creation,
            "user_id": self.user_id,
            "groupe_id": self.groupe_id,
        }
