class TicketHistory:
    def __init__(self, id=None, ticket_id=None, action=None, date_action=None):
        self.id = id
        self.ticket_id = ticket_id
        self.action = action
        self.date_action = date_action

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "action": self.action,
            "date_action": self.date_action,
        }
