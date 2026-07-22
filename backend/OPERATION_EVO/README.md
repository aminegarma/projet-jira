# Operation EVO — Démo Flask

Operation EVO est une application de démonstration pour la gestion et la supervision de tickets support. La version active utilise **Flask**, **SQLite**, des templates **Jinja/JavaScript** et une aide IA Mistral facultative.

Le dossier Angular présent dans le dépôt est conservé comme prototype historique. Il n'est pas nécessaire pour lancer la démo actuelle.

## Fonctions disponibles

- Connexion et déconnexion par session
- Deux espaces séparés : tableau de bord administrateur et espace utilisateur
- Redirection automatique selon le rôle après connexion
- Protection du tableau de bord et des API
- CRUD complet des tickets côté administrateur
- Création, consultation, modification et commentaires sur ses propres demandes côté utilisateur
- CRUD complet des utilisateurs, réservé à l'administrateur
- CRUD des groupes de problèmes, réservé à l'administrateur
- Affectation des tickets à un utilisateur
- Commentaires, historique et journal d'activité
- Classification IA ou heuristique des tickets
- Recherche de tickets similaires
- Suggestion d'affectation pour les groupes de problèmes
- Indicateurs de supervision et statistiques
- Export CSV et JSON
- Rapport hebdomadaire simulé lorsque SMTP n'est pas configuré

## Comptes de démonstration

Les comptes sont créés automatiquement au premier démarrage.

| Rôle | Email | Mot de passe |
|---|---|---|
| Administrateur | `admin@operation-evo.local` | `Admin123!` |
| Agent | `agent@operation-evo.local` | `Agent123!` |

Les mots de passe sont enregistrés sous forme hachée dans SQLite. Après connexion, l’administrateur arrive sur `/admin` et l’utilisateur sur `/dashboard`. Les comptes de démonstration sont réparés automatiquement au démarrage si leurs anciens hash ne correspondent pas aux mots de passe documentés.

## Installation sous Windows

### Prérequis

- Windows 10 ou 11
- Python 3.11 ou plus récent (Python 3.12 recommandé)
- Connexion Internet uniquement pour installer les dépendances la première fois

WSL et Ubuntu ne sont pas nécessaires.

### Méthode rapide

1. Ouvrir le dossier `backend\OPERATION_EVO`.
2. Double-cliquer sur `setup_windows.bat`.
3. Attendre la fin de l'installation.
4. Facultatif : double-cliquer sur `test_windows.bat` pour vérifier l’installation.
5. Double-cliquer sur `run_windows.bat`.
6. Le navigateur ouvre `http://127.0.0.1:5000/login`.

### Installation manuelle dans PowerShell

```powershell
cd backend\OPERATION_EVO
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
Copy-Item .env.example .env
cd backend
python app.py
```

Ouvrir ensuite :

```text
http://127.0.0.1:5000/login
```

## Configuration

Le fichier `.env.example` contient toutes les variables disponibles. Le script d'installation le copie en `.env` s'il n'existe pas.

### IA Mistral

La clé Mistral est facultative :

```env
MISTRAL_API_KEY=
```

Sans clé, l'application utilise automatiquement une classification heuristique locale. La démo reste donc fonctionnelle hors API Mistral.

### Email

Les paramètres SMTP sont facultatifs. Sans configuration SMTP, le rapport hebdomadaire est généré en mode simulé.

```env
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
```

Le worker automatique d'email est désactivé par défaut :

```env
DISABLE_EMAIL_WORKER=true
```

Le rapport peut toujours être déclenché manuellement depuis le tableau de bord.

## Organisation utile

```text
OPERATION_EVO/
├── .env.example
├── README.md
├── setup_windows.bat
├── run_windows.bat
└── backend/
    ├── app.py
    ├── config.py
    ├── requirements.txt
    ├── auth/
    ├── controllers/
    ├── database/
    ├── models/
    ├── routes/
    ├── services/
    ├── templates/
    └── tests/
```

## API principale

Toutes les routes ci-dessous, sauf la santé et la connexion, nécessitent une session active.

### Authentification

- `GET /login`
- `POST /login`
- `POST /logout`
- `GET /api/auth/me`
- `GET /api/health`

### Tickets

Pour un utilisateur standard, les routes de lecture sont limitées à ses propres tickets.

- `GET /api/tickets`
- `POST /api/tickets`
- `GET /api/tickets/<id>`
- `PUT /api/tickets/<id>`
- `DELETE /api/tickets/<id>` — administrateur
- `POST /api/tickets/<id>/assign` — administrateur
- `GET|POST /api/tickets/<id>/comments`
- `GET /api/tickets/<id>/activity`
- `GET /api/tickets/<id>/history`
- `GET /api/tickets/export?format=csv|json` — administrateur

### Utilisateurs

- `GET /api/users` — administrateur
- `GET /api/users/<id>`
- `POST /api/users` — administrateur
- `PUT /api/users/<id>` — administrateur
- `DELETE /api/users/<id>` — administrateur

### Groupes de problèmes

Toutes ces routes sont réservées à l’administrateur.

- `GET /api/tickets/problem-groups`
- `POST /api/tickets/problem-groups` — administrateur
- `GET /api/tickets/problem-groups/<id>` — administrateur
- `PUT /api/tickets/problem-groups/<id>` — administrateur
- `DELETE /api/tickets/problem-groups/<id>` — administrateur
- `GET /api/tickets/problem-groups/<id>/suggest-assignee` — administrateur

## Tests

Depuis le dossier `backend\OPERATION_EVO\backend` :

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Les tests couvrent notamment :

- classification et suggestions IA ;
- création, modification et suppression des tickets ;
- CRUD des utilisateurs ;
- CRUD des groupes de problèmes ;
- commentaires et activité ;
- historique et exports ;
- initialisation et conservation de la base ;
- génération du rapport hebdomadaire.

## Réinitialiser les données de démonstration

La base est créée dans `backend\data\app.db`.

Pour repartir du jeu de données initial, exécuter depuis `backend\OPERATION_EVO\backend` :

```powershell
python -c "from database.db import init_db; init_db(force=True)"
```

Cette commande supprime et recrée la base locale de démonstration.

## Limites assumées de la démo

- SQLite remplace une base serveur.
- La classification peut fonctionner par mots-clés sans Mistral.
- Le rapport email peut être simulé.
- La supervision est rafraîchie par appels HTTP, sans WebSocket.
- L'intégration Jira, PostgreSQL et Teams appartient à une phase ultérieure.

Ces simplifications sont volontaires afin de conserver une démonstration rapide, stable et facile à lancer sous Windows.
