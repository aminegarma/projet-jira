class ProblemeGroupe:
    def __init__(self, id=None, titre_probleme=None, ticket_maitre_id=None, statut=None, date_creation=None):
        self.id = id
        self.titre_probleme = titre_probleme
        self.ticket_maitre_id = ticket_maitre_id
        self.statut = statut
        self.date_creation = date_creation

    def to_dict(self):
        return {
            "id": self.id,
            "titre_probleme": self.titre_probleme,
            "ticket_maitre_id": self.ticket_maitre_id,
            "statut": self.statut,
            "date_creation": self.date_creation,
        }


class ProblemeUtilisateur:
    def __init__(self, id=None, groupe_id=None, user_id=None, date_signalement=None):
        self.id = id
        self.groupe_id = groupe_id
        self.user_id = user_id
        self.date_signalement = date_signalement

    def to_dict(self):
        return {
            "id": self.id,
            "groupe_id": self.groupe_id,
            "user_id": self.user_id,
            "date_signalement": self.date_signalement,
        }
