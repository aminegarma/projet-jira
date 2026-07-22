PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    poste TEXT,
    departement TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    active INTEGER NOT NULL DEFAULT 1,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS probleme_groupes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre_probleme TEXT NOT NULL,
    ticket_maitre_id INTEGER,
    statut TEXT DEFAULT 'ouvert',
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ticket_maitre_id) REFERENCES tickets(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    categorie TEXT,
    gravite TEXT,
    priorite TEXT,
    departement_cible TEXT,
    statut TEXT DEFAULT 'ouvert',
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    groupe_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(groupe_id) REFERENCES probleme_groupes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ticket_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    date_action TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ticket_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    user_id INTEGER,
    message TEXT NOT NULL,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ticket_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS probleme_utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    groupe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_signalement TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(groupe_id) REFERENCES probleme_groupes(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO users (id, nom, email, poste, departement, role, date_creation)
VALUES
    (1, 'Amina Benali', 'amina@example.com', 'Product Owner', 'Produit', 'admin', '2026-07-15 09:00:00'),
    (2, 'Karim Bensaid', 'karim@example.com', 'Support IT', 'IT', 'user', '2026-07-15 09:15:00'),
    (3, 'Lina Haddad', 'lina@example.com', 'Analyste', 'Finance', 'user', '2026-07-15 09:30:00'),
    (4, 'Sofiane Rahmoun', 'sofiane@example.com', 'Responsable RH', 'RH', 'manager', '2026-07-15 09:45:00'),
    (5, 'Nadia El Yacoubi', 'nadia@example.com', 'Ingénieure Support', 'IT', 'user', '2026-07-15 10:00:00'),
    (6, 'Youssef Ait Benali', 'youssef@example.com', 'Chef de projet', 'Produit', 'manager', '2026-07-15 10:15:00'),
    (7, 'Mariam Kacemi', 'mariam@example.com', 'Comptable', 'Finance', 'user', '2026-07-15 10:30:00'),
    (8, 'Hassan Mokrani', 'hassan@example.com', 'Responsable achats', 'Achats', 'manager', '2026-07-15 10:45:00'),
    (9, 'Salma Idrissi', 'salma@example.com', 'Développeuse', 'IT', 'user', '2026-07-15 11:00:00'),
    (10, 'Omar Tazi', 'omar@example.com', 'Administrateur systèmes', 'IT', 'admin', '2026-07-15 11:05:00'),
    (11, 'Rania El Hajj', 'rania@example.com', 'Analyste finance', 'Finance', 'user', '2026-07-15 11:10:00'),
    (12, 'Bilal Cherradi', 'bilal@example.com', 'Contrôleur de gestion', 'Finance', 'manager', '2026-07-15 11:15:00'),
    (13, 'Imane Boulahri', 'imane@example.com', 'Consultante RH', 'RH', 'user', '2026-07-15 11:20:00'),
    (14, 'Samir El Koudri', 'samir@example.com', 'Responsable qualité', 'Produit', 'manager', '2026-07-15 11:25:00'),
    (15, 'Leila Bouzidi', 'leila@example.com', 'Product Manager', 'Produit', 'user', '2026-07-15 11:30:00'),
    (16, 'Fouad Belkacem', 'fouad@example.com', 'Analyste achats', 'Achats', 'user', '2026-07-15 11:35:00'),
    (17, 'Chayma Jebali', 'chayma@example.com', 'Consultante support', 'IT', 'user', '2026-07-15 11:40:00'),
    (18, 'Walid Ben Youssef', 'walid@example.com', 'Responsable operations', 'Produit', 'manager', '2026-07-15 11:45:00'),
    (19, 'Mouna Sassi', 'mouna@example.com', 'Analyste RH', 'RH', 'user', '2026-07-15 11:50:00'),
    (20, 'Yacine Trabelsi', 'yacine@example.com', 'Ingénieur cloud', 'IT', 'user', '2026-07-15 12:00:00');

INSERT OR IGNORE INTO probleme_groupes (id, titre_probleme, ticket_maitre_id, statut, date_creation)
VALUES
    (1, 'Problème de connexion SSO', NULL, 'ouvert', '2026-07-15 10:00:00'),
    (2, 'Incident facturation', NULL, 'en_cours', '2026-07-15 10:15:00'),
    (3, 'Erreur d''affichage des rapports', NULL, 'ouvert', '2026-07-15 11:00:00'),
    (4, 'Latence sur l''API d''authentification', NULL, 'en_cours', '2026-07-15 12:10:00'),
    (5, 'Bogues sur la génération des exportations', NULL, 'ouvert', '2026-07-15 12:20:00');

INSERT OR IGNORE INTO tickets (id, titre, description, categorie, gravite, priorite, departement_cible, statut, date_creation, user_id, groupe_id)
VALUES
    (1, 'Erreur de connexion', 'L''utilisateur ne parvient pas à se connecter au portail', 'access', 'haute', 'urgent', 'IT', 'ouvert', '2026-07-15 10:05:00', 2, 1),
    (2, 'Facture introuvable', 'La facture n''apparaît pas dans l''interface', 'facturation', 'moyenne', 'normal', 'Finance', 'en_cours', '2026-07-15 10:20:00', 3, 2),
    (3, 'Bug interface tableau de bord', 'Le tableau de bord affiche des données partielles', 'bug', 'moyenne', 'normal', 'Produit', 'resolu', '2026-07-15 10:35:00', 1, NULL),
    (4, 'Demande de droits', 'Besoin d''accès à l''application RH', 'access', 'faible', 'faible', 'RH', 'ouvert', '2026-07-15 10:45:00', 2, NULL),
    (5, 'Erreur d''impression', 'Une impression de document échoue sur l''imprimante réseau', 'impression', 'moyenne', 'normal', 'IT', 'ouvert', '2026-07-15 11:00:00', 5, NULL),
    (6, 'Réinitialisation mot de passe', 'L''utilisateur ne reçoit pas l''email de réinitialisation', 'access', 'moyenne', 'normal', 'IT', 'en_cours', '2026-07-15 11:10:00', 5, NULL),
    (7, 'Demande de modification du contrat', 'Besoin de mettre à jour les informations du contrat', 'contrat', 'faible', 'faible', 'RH', 'resolu', '2026-07-15 11:20:00', 4, NULL),
    (8, 'Achat non réceptionné', 'Un bon de commande n''est pas visible dans le système', 'achats', 'moyenne', 'normal', 'Achats', 'ouvert', '2026-07-15 11:30:00', 8, NULL),
    (9, 'Erreur de calcul de salaire', 'Le calcul du bulletin ne se termine pas', 'payroll', 'haute', 'urgent', 'Finance', 'ouvert', '2026-07-15 11:40:00', 7, NULL),
    (10, 'Rapport incomplet', 'Un rapport exporté manque de plusieurs colonnes', 'rapport', 'moyenne', 'normal', 'Produit', 'en_cours', '2026-07-15 11:50:00', 6, 3),
    (11, 'Problème de synchronisation', 'Les données ne se synchronisent pas entre les modules', 'integration', 'haute', 'urgent', 'IT', 'ouvert', '2026-07-15 12:00:00', 2, NULL),
    (12, 'Facture en attente', 'Les factures ne sont pas traitées dans le délai', 'facturation', 'moyenne', 'normal', 'Finance', 'resolu', '2026-07-15 12:10:00', 3, NULL),
    (13, 'Demande d''accès au portail RH', 'Un nouveau collaborateur a besoin d''un accès', 'access', 'faible', 'faible', 'RH', 'ouvert', '2026-07-15 12:20:00', 4, NULL),
    (14, 'Erreur manifeste', 'Le fichier manifeste est corrompu', 'bug', 'haute', 'urgent', 'Produit', 'en_cours', '2026-07-15 12:30:00', 1, NULL),
    (15, 'Retard de livraison', 'Un colis n''est pas encore livré au client', 'logistique', 'moyenne', 'normal', 'Achats', 'ouvert', '2026-07-15 12:40:00', 8, NULL),
    (16, 'Connexion SSO bloquée', 'Les utilisateurs du département IT ne peuvent plus se connecter via SSO après la mise à jour', 'access', 'haute', 'urgent', 'IT', 'ouvert', '2026-07-15 13:00:00', 9, 1),
    (17, 'MFA non affiché', 'Le prompt MFA n''apparaît pas pour certains comptes après l''authentification', 'access', 'moyenne', 'normal', 'IT', 'en_cours', '2026-07-15 13:10:00', 10, 1),
    (18, 'Session expirée trop tôt', 'Les sessions expirent très rapidement sur l''application interne', 'access', 'moyenne', 'normal', 'Produit', 'ouvert', '2026-07-15 13:15:00', 14, 1),
    (19, 'Réinitialisation impossible', 'La réinitialisation du mot de passe échoue après validation du formulaire', 'access', 'faible', 'faible', 'RH', 'ouvert', '2026-07-15 13:20:00', 13, 1),
    (20, 'Connexion mobile impossible', 'L''accès mobile échoue sur iOS après la dernière mise à jour', 'access', 'moyenne', 'normal', 'Produit', 'ouvert', '2026-07-15 13:25:00', 15, 1),
    (21, 'Token invalide', 'Le token d''authentification est refusé même après renouvellement', 'access', 'haute', 'urgent', 'Finance', 'en_cours', '2026-07-15 13:30:00', 11, 1),
    (22, 'Latence API de login', 'L''API de login répond de façon intermittente', 'access', 'haute', 'urgent', 'IT', 'ouvert', '2026-07-15 13:40:00', 17, 4),
    (23, 'Erreur sur le cache SSO', 'Le cache SSO ne se met plus à jour après déconnexion', 'access', 'moyenne', 'normal', 'IT', 'en_cours', '2026-07-15 13:50:00', 20, 4),
    (24, 'Export CSV incomplet', 'L''export CSV manque plusieurs lignes sur certains rapports', 'rapport', 'moyenne', 'normal', 'Produit', 'ouvert', '2026-07-15 14:00:00', 18, 5),
    (25, 'Export PDF non généré', 'Le PDF n''est pas généré après validation du rapport', 'rapport', 'haute', 'urgent', 'Produit', 'en_cours', '2026-07-15 14:10:00', 6, 5),
    (26, 'Mise à jour de la bibliothèque d''exports', 'Les exportations échouent après la mise à jour du package', 'bug', 'moyenne', 'normal', 'Produit', 'ouvert', '2026-07-15 14:20:00', 14, 5),
    (27, 'Demande d''accès au portail de reporting', 'Nouveau besoin d''accès pour l''équipe reporting', 'access', 'faible', 'faible', 'Produit', 'ouvert', '2026-07-15 14:30:00', 19, NULL);

UPDATE probleme_groupes SET ticket_maitre_id = 1 WHERE id = 1;
UPDATE probleme_groupes SET ticket_maitre_id = 2 WHERE id = 2;
UPDATE probleme_groupes SET ticket_maitre_id = 10 WHERE id = 3;
UPDATE probleme_groupes SET ticket_maitre_id = 22 WHERE id = 4;
UPDATE probleme_groupes SET ticket_maitre_id = 24 WHERE id = 5;

INSERT OR IGNORE INTO ticket_history (id, ticket_id, action, date_action)
VALUES
    (1, 1, 'créé', '2026-07-15 10:05:00'),
    (2, 1, 'assigné', '2026-07-15 10:10:00'),
    (3, 2, 'créé', '2026-07-15 10:20:00'),
    (4, 5, 'créé', '2026-07-15 11:00:00'),
    (5, 6, 'assigné', '2026-07-15 11:10:00'),
    (6, 10, 'créé', '2026-07-15 11:50:00'),
    (7, 22, 'créé', '2026-07-15 13:40:00'),
    (8, 24, 'créé', '2026-07-15 14:00:00'),
    (9, 25, 'assigné', '2026-07-15 14:10:00');

INSERT OR IGNORE INTO probleme_utilisateurs (id, groupe_id, user_id, date_signalement)
VALUES
    (1, 1, 2, '2026-07-15 10:06:00'),
    (2, 2, 3, '2026-07-15 10:22:00'),
    (3, 3, 6, '2026-07-15 11:01:00'),
    (4, 4, 17, '2026-07-15 12:12:00'),
    (5, 4, 20, '2026-07-15 12:14:00'),
    (6, 5, 18, '2026-07-15 12:23:00'),
    (7, 5, 14, '2026-07-15 12:25:00');
