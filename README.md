# Backend Flask – Guide de démarrage

Ce dossier contient une API Flask de base avec une structure MVC pour gérer les utilisateurs, les tickets et les statistiques.

## Prérequis

- Python 3.10+ installé
- PowerShell ou terminal disponible
- Accès au dossier du projet

## 1. Se placer dans le dossier backend

```powershell
cd .\backend
```

## 2. Créer et activer l’environnement virtuel

Si le dossier venv n’existe pas encore :

```powershell
python -m venv venv
```

Pour l’activer sous Windows PowerShell :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Si l’activation bloque encore, utilisez la commande suivante dans la même fenêtre PowerShell :

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

## 3. Créer le fichier .env

Le fichier .env n’est pas versionné dans Git. À la racine du dossier backend, créez un fichier nommé .env avec ce contenu :

```env
MISTRAL_API_KEY=votre_clé_ici
```

> Demandez la clé à l’administrateur du projet si vous n’en avez pas.

## 4. Installer les dépendances

Avec le venv activé :

```powershell
pip install -r requirements.txt
```

Si l’activation a échoué à l’étape 2, utilisez plutôt :

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Lancer l’application

Avec le venv activé :

```powershell
python app.py
```

Si l’activation a échoué à l’étape 2, utilisez plutôt :

```powershell
.\venv\Scripts\python.exe app.py
```

L’API sera disponible à l’adresse :

- http://127.0.0.1:5000

## 6. Tester l’API

Dans un autre terminal :

```powershell
curl http://127.0.0.1:5000/api/health
```

Résultat attendu :

```json
{"status": "ok"}
```

Autres routes disponibles :

```powershell
curl http://127.0.0.1:5000/api/users
curl http://127.0.0.1:5000/api/tickets
curl http://127.0.0.1:5000/api/stats
```

## 7. Structure du backend

- app.py : point d’entrée Flask
- config.py : configuration globale
- controllers/ : logique applicative
- routes/ : blueprints Flask
- models/ : classes métier
- services/ : intégration Mistral / logique de similarité
- database/ : base SQLite et script d’initialisation
- data/app.db : base SQLite locale

## 8. Notes importantes

- Le fichier .env doit être créé manuellement par chaque développeur — il n’est jamais commité sur Git.
- La base SQLite est créée automatiquement au premier lancement si elle n’existe pas.
- Le dossier venv/ ne doit jamais être ajouté à Git (déjà exclu via .gitignore).

## 9. Arrêter le serveur

Dans le terminal où le serveur tourne, appuyez sur :

```powershell
Ctrl + C
```
