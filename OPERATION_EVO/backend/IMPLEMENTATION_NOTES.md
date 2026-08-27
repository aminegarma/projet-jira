# Changements implémentés

## Authentification

- Connexion par email et mot de passe
- Sessions Flask-Login
- Déconnexion
- Protection du dashboard et des API
- Comptes administrateur et agent initialisés automatiquement
- Mots de passe hachés
- Décorateur d'autorisation administrateur

## CRUD

- Tickets : création, lecture, modification complète et suppression
- Utilisateurs : création, lecture, modification et suppression
- Groupes de problèmes : création, lecture, modification et suppression
- Validations métier et codes HTTP cohérents
- Contrôle des références vers les utilisateurs, tickets et groupes

## Dashboard

- Interface réorganisée et responsive
- Formulaires modaux réutilisables
- Gestion des erreurs et chargements
- Actualisation après chaque opération
- Commentaires et activité des tickets
- Exports CSV/JSON
- Administration des utilisateurs et groupes selon le rôle

## IA et supervision

- Classification Mistral facultative avec repli heuristique
- Suggestion d'affectation réelle utilisée par l'interface
- Tickets similaires et synthèses de groupes
- Statistiques et rapport hebdomadaire

## Sécurité adaptée à la démo

- Suppression du PIN exposé dans le navigateur
- Suppressions contrôlées côté serveur par rôle
- Échappement du contenu affiché dans le HTML
- Variables sensibles déplacées vers `.env`
- Worker email désactivé par défaut

## Correctif de connexion (v2)
- Les mots de passe des comptes de démonstration sont désormais vérifiés et réparés automatiquement au démarrage si le hash fourni est ancien ou incompatible.
- `repair_login.bat` permet d'appliquer le correctif sans supprimer les tickets ni les autres données.

## Séparation des rôles et dashboards (v3)
- Redirection automatique de l'administrateur vers `/admin`.
- Redirection automatique de l'utilisateur ou du manager vers `/dashboard`.
- Nouveau template `templates/user_dashboard.html` pour les demandes personnelles.
- Filtrage serveur des tickets sur l'utilisateur connecté.
- Contrôle d'accès ticket par ticket pour la lecture, la modification, les commentaires et l'activité.
- Routes globales (utilisateurs, groupes, statistiques, export, affectation) réservées à l'administrateur.
- Ajout automatique d'une demande de démonstration au compte utilisateur lorsqu'il n'en possède aucune.
