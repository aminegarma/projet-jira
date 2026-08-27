# Operation EVO

Plateforme Flask de gestion de tickets, supervision d'incidents et aide à la décision par IA.

## À lire en premier

La démo active est backend-first (Flask/Jinja). Le prototype Angular dans [frontend](frontend) est conservé mais n'est pas nécessaire pour lancer la démo.

Dépendances Python: un seul fichier est utilisé dans ce dépôt, [backend/requirements.txt](backend/requirements.txt).

## Démarrage rapide sous Windows

1. Ouvrir le dossier [backend](backend).
2. Exécuter [backend/setup_windows.bat](backend/setup_windows.bat) une seule fois.
3. Exécuter [backend/run_windows.bat](backend/run_windows.bat) pour lancer l'application.

## Comptes de démonstration

- Administrateur: admin@operation-evo.local / Admin123!
- Utilisateur: agent@operation-evo.local / Agent123!

Après connexion:

- Administrateur -> /admin
- Utilisateur -> /dashboard

## Démarrage manuel (alternative)

```powershell
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Sous PowerShell, si l'activation échoue (politique d'exécution):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Fonctionnalités

- Gestion et affectation des tickets, groupes de problèmes
- Supervision temps réel (métriques, historique, commentaires)
- Suggestions IA (tickets similaires, priorisation)
- Export CSV/JSON, envoi d'email de synthèse

## Accès

- Dashboard admin: http://127.0.0.1:5000/admin
- Login: http://127.0.0.1:5000/login
- Santé API: http://127.0.0.1:5000/api/health

Liste complète des URLs: [URLS.md](URLS.md)

## Documentation complète

Consulter [backend/README.md](backend/README.md).