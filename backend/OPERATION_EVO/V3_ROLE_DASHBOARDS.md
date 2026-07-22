# Correctif V3 — séparation administrateur / utilisateur

Cette version corrige le comportement où tous les comptes étaient redirigés vers `/admin`.

## Comportement attendu

- Administrateur : connexion vers `/admin`
- Utilisateur ou manager : connexion vers `/dashboard`
- Un utilisateur qui tente d'ouvrir `/admin` est redirigé vers `/dashboard`
- Le tableau de bord utilisateur ne charge ni la liste complète des utilisateurs, ni les groupes, ni les métriques administrateur
- `GET /api/tickets` est filtré côté serveur sur l'utilisateur connecté
- Un utilisateur ne peut pas lire ou modifier le ticket d'un autre utilisateur
- Affectation, suppression, export, groupes et statistiques globales sont réservés à l'administrateur

## Espace utilisateur

L'espace `/dashboard` permet de :

- consulter ses propres demandes ;
- créer une demande ;
- modifier le titre, la description et le statut de sa demande ;
- consulter les détails et l'activité ;
- ajouter des commentaires ;
- filtrer et rechercher ses demandes.

Un ticket de démonstration est ajouté automatiquement au compte utilisateur si celui-ci ne possède encore aucun ticket.
