import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, delay, map, of } from 'rxjs';
import {
  DashboardStats,
  ProblemGroup,
  Ticket,
  TicketActivity,
  TicketAssignPayload,
  TicketComment,
  TicketCommentPayload,
  TicketCreatePayload,
  TicketFilters,
  TicketHistory,
  TicketPriorite,
  TicketStatut,
  TicketUpdateStatusPayload,
  User
} from '../models/item';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly apiBaseUrl = 'http://localhost:5000/api';
  private readonly mockLatencyMs = 280;
  private readonly useMockData = true;

  private tickets: Ticket[] = [
    {
      id: 1,
      titre: 'Erreur de connexion',
      description: "L'utilisateur ne parvient pas à se connecter au portail",
      categorie: 'access',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'IT',
      statut: 'ouvert',
      date_creation: '2026-07-15T10:05:00Z',
      user_id: 2,
      groupe_id: 1,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Karim Bensaid',
      reporter_email: 'karim@example.com'
    },
    {
      id: 2,
      titre: 'Facture introuvable',
      description: "La facture n'apparaît pas dans l'interface",
      categorie: 'facturation',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Finance',
      statut: 'en_cours',
      date_creation: '2026-07-15T10:20:00Z',
      user_id: 3,
      groupe_id: 2,
      assignee_user_id: 11,
      assignee_name: 'Rania El Hajj',
      reporter_name: 'Lina Haddad',
      reporter_email: 'lina@example.com'
    },
    {
      id: 3,
      titre: 'Bug interface tableau de bord',
      description: 'Le tableau de bord affiche des données partielles',
      categorie: 'bug',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'resolu',
      date_creation: '2026-07-15T10:35:00Z',
      user_id: 1,
      groupe_id: null,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Amina Benali',
      reporter_email: 'amina@example.com'
    },
    {
      id: 4,
      titre: 'Demande de droits',
      description: "Besoin d'accès à l'application RH",
      categorie: 'access',
      gravite: 'faible',
      priorite: 'faible',
      departement_cible: 'RH',
      statut: 'ouvert',
      date_creation: '2026-07-15T10:45:00Z',
      user_id: 2,
      groupe_id: null,
      assignee_user_id: 13,
      assignee_name: 'Imane Boulahri',
      reporter_name: 'Karim Bensaid',
      reporter_email: 'karim@example.com'
    },
    {
      id: 5,
      titre: 'Erreur d\'impression',
      description: "Une impression de document échoue sur l'imprimante réseau",
      categorie: 'impression',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'IT',
      statut: 'ouvert',
      date_creation: '2026-07-15T11:00:00Z',
      user_id: 5,
      groupe_id: null,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Nadia El Yacoubi',
      reporter_email: 'nadia@example.com'
    },
    {
      id: 6,
      titre: 'Réinitialisation mot de passe',
      description: "L'utilisateur ne reçoit pas l'email de réinitialisation",
      categorie: 'access',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'IT',
      statut: 'en_cours',
      date_creation: '2026-07-15T11:10:00Z',
      user_id: 5,
      groupe_id: null,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Nadia El Yacoubi',
      reporter_email: 'nadia@example.com'
    },
    {
      id: 7,
      titre: 'Demande de modification du contrat',
      description: "Besoin de mettre à jour les informations du contrat",
      categorie: 'contrat',
      gravite: 'faible',
      priorite: 'faible',
      departement_cible: 'RH',
      statut: 'resolu',
      date_creation: '2026-07-15T11:20:00Z',
      user_id: 4,
      groupe_id: null,
      assignee_user_id: 13,
      assignee_name: 'Imane Boulahri',
      reporter_name: 'Sofiane Rahmoun',
      reporter_email: 'sofiane@example.com'
    },
    {
      id: 8,
      titre: 'Achat non réceptionné',
      description: "Un bon de commande n'est pas visible dans le système",
      categorie: 'achats',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Achats',
      statut: 'ouvert',
      date_creation: '2026-07-15T11:30:00Z',
      user_id: 8,
      groupe_id: null,
      assignee_user_id: 8,
      assignee_name: 'Hassan Mokrani',
      reporter_name: 'Hassan Mokrani',
      reporter_email: 'hassan@example.com'
    },
    {
      id: 9,
      titre: 'Erreur de calcul de salaire',
      description: 'Le calcul du bulletin ne se termine pas',
      categorie: 'payroll',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'Finance',
      statut: 'ouvert',
      date_creation: '2026-07-15T11:40:00Z',
      user_id: 7,
      groupe_id: null,
      assignee_user_id: 11,
      assignee_name: 'Rania El Hajj',
      reporter_name: 'Mariam Kacemi',
      reporter_email: 'mariam@example.com'
    },
    {
      id: 10,
      titre: 'Rapport incomplet',
      description: 'Un rapport exporté manque de plusieurs colonnes',
      categorie: 'rapport',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'en_cours',
      date_creation: '2026-07-15T11:50:00Z',
      user_id: 6,
      groupe_id: 3,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Youssef Ait Benali',
      reporter_email: 'youssef@example.com'
    },
    {
      id: 11,
      titre: 'Problème de synchronisation',
      description: 'Les données ne se synchronisent pas entre les modules',
      categorie: 'integration',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'IT',
      statut: 'ouvert',
      date_creation: '2026-07-15T12:00:00Z',
      user_id: 2,
      groupe_id: null,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Karim Bensaid',
      reporter_email: 'karim@example.com'
    },
    {
      id: 12,
      titre: 'Facture en attente',
      description: 'Les factures ne sont pas traitées dans le délai',
      categorie: 'facturation',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Finance',
      statut: 'resolu',
      date_creation: '2026-07-15T12:10:00Z',
      user_id: 3,
      groupe_id: null,
      assignee_user_id: 11,
      assignee_name: 'Rania El Hajj',
      reporter_name: 'Lina Haddad',
      reporter_email: 'lina@example.com'
    },
    {
      id: 13,
      titre: 'Demande d\'accès au portail RH',
      description: "Un nouveau collaborateur a besoin d'un accès",
      categorie: 'access',
      gravite: 'faible',
      priorite: 'faible',
      departement_cible: 'RH',
      statut: 'ouvert',
      date_creation: '2026-07-15T12:20:00Z',
      user_id: 4,
      groupe_id: null,
      assignee_user_id: 13,
      assignee_name: 'Imane Boulahri',
      reporter_name: 'Sofiane Rahmoun',
      reporter_email: 'sofiane@example.com'
    },
    {
      id: 14,
      titre: 'Erreur manifeste',
      description: 'Le fichier manifeste est corrompu',
      categorie: 'bug',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'Produit',
      statut: 'en_cours',
      date_creation: '2026-07-15T12:30:00Z',
      user_id: 1,
      groupe_id: null,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Amina Benali',
      reporter_email: 'amina@example.com'
    },
    {
      id: 15,
      titre: 'Retard de livraison',
      description: "Un colis n'est pas encore livré au client",
      categorie: 'logistique',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Achats',
      statut: 'ouvert',
      date_creation: '2026-07-15T12:40:00Z',
      user_id: 8,
      groupe_id: null,
      assignee_user_id: 8,
      assignee_name: 'Hassan Mokrani',
      reporter_name: 'Hassan Mokrani',
      reporter_email: 'hassan@example.com'
    },
    {
      id: 16,
      titre: 'Connexion SSO bloquée',
      description: 'Les utilisateurs du département IT ne peuvent plus se connecter via SSO après la mise à jour',
      categorie: 'access',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'IT',
      statut: 'ouvert',
      date_creation: '2026-07-15T13:00:00Z',
      user_id: 9,
      groupe_id: 1,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Salma Idrissi',
      reporter_email: 'salma@example.com'
    },
    {
      id: 17,
      titre: 'MFA non affiché',
      description: "Le prompt MFA n'apparaît pas pour certains comptes après l'authentification",
      categorie: 'access',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'IT',
      statut: 'en_cours',
      date_creation: '2026-07-15T13:10:00Z',
      user_id: 10,
      groupe_id: 1,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Omar Tazi',
      reporter_email: 'omar@example.com'
    },
    {
      id: 18,
      titre: 'Session expirée trop tôt',
      description: "Les sessions expirent très rapidement sur l'application interne",
      categorie: 'access',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'ouvert',
      date_creation: '2026-07-15T13:15:00Z',
      user_id: 14,
      groupe_id: 1,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Samir El Koudri',
      reporter_email: 'samir@example.com'
    },
    {
      id: 19,
      titre: 'Réinitialisation impossible',
      description: 'La réinitialisation du mot de passe échoue après validation du formulaire',
      categorie: 'access',
      gravite: 'faible',
      priorite: 'faible',
      departement_cible: 'RH',
      statut: 'ouvert',
      date_creation: '2026-07-15T13:20:00Z',
      user_id: 13,
      groupe_id: 1,
      assignee_user_id: 13,
      assignee_name: 'Imane Boulahri',
      reporter_name: 'Imane Boulahri',
      reporter_email: 'imane@example.com'
    },
    {
      id: 20,
      titre: 'Connexion mobile impossible',
      description: "L'accès mobile échoue sur iOS après la dernière mise à jour",
      categorie: 'access',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'ouvert',
      date_creation: '2026-07-15T13:25:00Z',
      user_id: 15,
      groupe_id: 1,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Leila Bouzidi',
      reporter_email: 'leila@example.com'
    },
    {
      id: 21,
      titre: 'Token invalide',
      description: "Le token d'authentification est refusé même après renouvellement",
      categorie: 'access',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'Finance',
      statut: 'en_cours',
      date_creation: '2026-07-15T13:30:00Z',
      user_id: 11,
      groupe_id: 1,
      assignee_user_id: 11,
      assignee_name: 'Rania El Hajj',
      reporter_name: 'Rania El Hajj',
      reporter_email: 'rania@example.com'
    },
    {
      id: 22,
      titre: 'Latence API de login',
      description: "L'API de login répond de façon intermittente",
      categorie: 'access',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'IT',
      statut: 'ouvert',
      date_creation: '2026-07-15T13:40:00Z',
      user_id: 17,
      groupe_id: 4,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Chayma Jebali',
      reporter_email: 'chayma@example.com'
    },
    {
      id: 23,
      titre: 'Erreur sur le cache SSO',
      description: 'Le cache SSO ne se met plus à jour après déconnexion',
      categorie: 'access',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'IT',
      statut: 'en_cours',
      date_creation: '2026-07-15T13:50:00Z',
      user_id: 20,
      groupe_id: 4,
      assignee_user_id: 10,
      assignee_name: 'Omar Tazi',
      reporter_name: 'Yacine Trabelsi',
      reporter_email: 'yacine@example.com'
    },
    {
      id: 24,
      titre: 'Export CSV incomplet',
      description: "L'export CSV manque plusieurs lignes sur certains rapports",
      categorie: 'rapport',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'ouvert',
      date_creation: '2026-07-15T14:00:00Z',
      user_id: 18,
      groupe_id: 5,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Walid Ben Youssef',
      reporter_email: 'walid@example.com'
    },
    {
      id: 25,
      titre: 'Export PDF non généré',
      description: 'Le PDF n\'est pas généré après validation du rapport',
      categorie: 'rapport',
      gravite: 'haute',
      priorite: 'urgent',
      departement_cible: 'Produit',
      statut: 'en_cours',
      date_creation: '2026-07-15T14:10:00Z',
      user_id: 6,
      groupe_id: 5,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Youssef Ait Benali',
      reporter_email: 'youssef@example.com'
    },
    {
      id: 26,
      titre: 'Mise à jour de la bibliothèque d\'exports',
      description: 'Les exportations échouent après la mise à jour du package',
      categorie: 'bug',
      gravite: 'moyenne',
      priorite: 'normal',
      departement_cible: 'Produit',
      statut: 'ouvert',
      date_creation: '2026-07-15T14:20:00Z',
      user_id: 14,
      groupe_id: 5,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Samir El Koudri',
      reporter_email: 'samir@example.com'
    },
    {
      id: 27,
      titre: 'Demande d\'accès au portail de reporting',
      description: 'Nouveau besoin d\'accès pour l\'équipe reporting',
      categorie: 'access',
      gravite: 'faible',
      priorite: 'faible',
      departement_cible: 'Produit',
      statut: 'ouvert',
      date_creation: '2026-07-15T14:30:00Z',
      user_id: 19,
      groupe_id: null,
      assignee_user_id: 6,
      assignee_name: 'Youssef Ait Benali',
      reporter_name: 'Mouna Sassi',
      reporter_email: 'mouna@example.com'
    }
  ];

  private users: User[] = [
    { id: 1, nom: 'Amina Benali', email: 'amina@example.com', poste: 'Product Owner', departement: 'Produit', role: 'admin', date_creation: '2026-07-15 09:00:00' },
    { id: 2, nom: 'Karim Bensaid', email: 'karim@example.com', poste: 'Support IT', departement: 'IT', role: 'user', date_creation: '2026-07-15 09:15:00' },
    { id: 3, nom: 'Lina Haddad', email: 'lina@example.com', poste: 'Analyste', departement: 'Finance', role: 'user', date_creation: '2026-07-15 09:30:00' },
    { id: 4, nom: 'Sofiane Rahmoun', email: 'sofiane@example.com', poste: 'Responsable RH', departement: 'RH', role: 'manager', date_creation: '2026-07-15 09:45:00' },
    { id: 5, nom: 'Nadia El Yacoubi', email: 'nadia@example.com', poste: 'Ingénieure Support', departement: 'IT', role: 'user', date_creation: '2026-07-15 10:00:00' },
    { id: 6, nom: 'Youssef Ait Benali', email: 'youssef@example.com', poste: 'Chef de projet', departement: 'Produit', role: 'manager', date_creation: '2026-07-15 10:15:00' },
    { id: 7, nom: 'Mariam Kacemi', email: 'mariam@example.com', poste: 'Comptable', departement: 'Finance', role: 'user', date_creation: '2026-07-15 10:30:00' },
    { id: 8, nom: 'Hassan Mokrani', email: 'hassan@example.com', poste: 'Responsable achats', departement: 'Achats', role: 'manager', date_creation: '2026-07-15 10:45:00' },
    { id: 9, nom: 'Salma Idrissi', email: 'salma@example.com', poste: 'Développeuse', departement: 'IT', role: 'user', date_creation: '2026-07-15 11:00:00' },
    { id: 10, nom: 'Omar Tazi', email: 'omar@example.com', poste: 'Administrateur systèmes', departement: 'IT', role: 'admin', date_creation: '2026-07-15 11:05:00' },
    { id: 11, nom: 'Rania El Hajj', email: 'rania@example.com', poste: 'Analyste finance', departement: 'Finance', role: 'user', date_creation: '2026-07-15 11:10:00' },
    { id: 12, nom: 'Bilal Cherradi', email: 'bilal@example.com', poste: 'Contrôleur de gestion', departement: 'Finance', role: 'manager', date_creation: '2026-07-15 11:15:00' },
    { id: 13, nom: 'Imane Boulahri', email: 'imane@example.com', poste: 'Consultante RH', departement: 'RH', role: 'user', date_creation: '2026-07-15 11:20:00' },
    { id: 14, nom: 'Samir El Koudri', email: 'samir@example.com', poste: 'Responsable qualité', departement: 'Produit', role: 'manager', date_creation: '2026-07-15 11:25:00' },
    { id: 15, nom: 'Leila Bouzidi', email: 'leila@example.com', poste: 'Product Manager', departement: 'Produit', role: 'user', date_creation: '2026-07-15 11:30:00' },
    { id: 16, nom: 'Fouad Belkacem', email: 'fouad@example.com', poste: 'Analyste achats', departement: 'Achats', role: 'user', date_creation: '2026-07-15 11:35:00' },
    { id: 17, nom: 'Chayma Jebali', email: 'chayma@example.com', poste: 'Consultante support', departement: 'IT', role: 'user', date_creation: '2026-07-15 11:40:00' },
    { id: 18, nom: 'Walid Ben Youssef', email: 'walid@example.com', poste: 'Responsable operations', departement: 'Produit', role: 'manager', date_creation: '2026-07-15 11:45:00' },
    { id: 19, nom: 'Mouna Sassi', email: 'mouna@example.com', poste: 'Analyste RH', departement: 'RH', role: 'user', date_creation: '2026-07-15 11:50:00' },
    { id: 20, nom: 'Yacine Trabelsi', email: 'yacine@example.com', poste: 'Ingénieur cloud', departement: 'IT', role: 'user', date_creation: '2026-07-15 12:00:00' }
  ];

  private problemGroups: ProblemGroup[] = [
    { id: 1, titre_probleme: 'Problème de connexion SSO', ticket_maitre_id: 1, statut: 'ouvert', date_creation: '2026-07-15 10:00:00' },
    { id: 2, titre_probleme: 'Incident facturation', ticket_maitre_id: 2, statut: 'en_cours', date_creation: '2026-07-15 10:15:00' },
    { id: 3, titre_probleme: 'Erreur d\'affichage des rapports', ticket_maitre_id: 3, statut: 'ouvert', date_creation: '2026-07-15 11:00:00' }
  ];

  private ticketHistory: TicketHistory[] = [
    { id: 1, ticket_id: 1, action: 'créé', date_action: '2026-07-15 10:05:00' },
    { id: 2, ticket_id: 1, action: 'assigné', date_action: '2026-07-15 10:10:00' },
    { id: 3, ticket_id: 2, action: 'créé', date_action: '2026-07-15 10:20:00' }
  ];

  private ticketComments: TicketComment[] = [
    { id: 1, ticket_id: 1, user_id: 2, message: 'Le problème est reproductible sur le portail interne.', date_creation: '2026-07-15 10:06:00' },
    { id: 2, ticket_id: 2, user_id: 3, message: 'Pièce jointe manquante dans le dossier utilisateur.', date_creation: '2026-07-15 10:22:00' }
  ];

  private ticketActivity: TicketActivity[] = [
    { id: 1, ticket_id: 1, action: 'created', details: 'Ticket créé via formulaire web', created_at: '2026-07-15 10:05:00' },
    { id: 2, ticket_id: 1, action: 'assigned', details: 'Assigné à Omar Tazi', created_at: '2026-07-15 10:10:00' }
  ];

  constructor(private readonly http: HttpClient) {}

  getTickets(filters: TicketFilters = {}): Observable<Ticket[]> {
    if (!this.useMockData) {
      return this.http.get<Ticket[]>(`${this.apiBaseUrl}/tickets`, { params: this.toHttpParams(filters) }).pipe(
        catchError(() => this.simulateResponse(() => this.applyTicketFilters([...this.tickets], filters)))
      );
    }

    return this.simulateResponse(() => this.applyTicketFilters([...this.tickets], filters));
  }

  getTicketById(id: number): Observable<Ticket | undefined> {
    if (!this.useMockData) {
      return this.http.get<Ticket>(`${this.apiBaseUrl}/tickets/${id}`).pipe(
        map((item) => item ?? undefined),
        catchError(() => this.simulateResponse(() => this.tickets.find((item) => item.id === id)))
      );
    }

    return this.simulateResponse(() => this.tickets.find((item) => item.id === id));
  }

  createTicket(payload: TicketCreatePayload): Observable<Ticket> {
    if (!this.useMockData) {
      return this.http.post<Ticket>(`${this.apiBaseUrl}/tickets`, payload);
    }

    return this.simulateResponse(() => {
      const now = new Date().toISOString();
      const ticket: Ticket = {
        id: this.nextId(),
        titre: payload.titre.trim(),
        description: payload.description.trim(),
        categorie: payload.categorie.trim(),
        gravite: payload.gravite,
        priorite: payload.priorite,
        departement_cible: payload.departement_cible.trim(),
        statut: 'ouvert',
        date_creation: now,
        user_id: payload.user_id ?? null,
        groupe_id: this.deriveGroupId(payload),
        assignee_user_id: this.deriveAssigneeUserId(payload),
        assignee_name: this.deriveAssigneeName(payload),
        reporter_name: this.resolveReporterName(payload.user_id ?? null),
        reporter_email: this.resolveReporterEmail(payload.user_id ?? null)
      };

      this.tickets = [ticket, ...this.tickets];
      return ticket;
    });
  }

  updateTicketStatus(id: number, payload: TicketUpdateStatusPayload): Observable<Ticket> {
    if (!this.useMockData) {
      return this.http.patch<Ticket>(`${this.apiBaseUrl}/tickets/${id}/status`, payload);
    }

    return this.simulateResponse(() => {
      const itemIndex = this.tickets.findIndex((entry) => entry.id === id);

      if (itemIndex === -1) {
        throw new Error(`Item ${id} introuvable`);
      }

      const updatedItem = {
        ...this.tickets[itemIndex],
        statut: payload.statut
      };

      this.tickets = [
        ...this.tickets.slice(0, itemIndex),
        updatedItem,
        ...this.tickets.slice(itemIndex + 1)
      ];

      return updatedItem;
    });
  }

  updateTicketAssignment(id: number, payload: TicketAssignPayload): Observable<Ticket> {
    if (!this.useMockData) {
      return this.http.patch<Ticket>(`${this.apiBaseUrl}/tickets/${id}/assignment`, payload);
    }

    return this.simulateResponse(() => {
      const ticketIndex = this.tickets.findIndex((entry) => entry.id === id);

      if (ticketIndex === -1) {
        throw new Error(`Ticket ${id} introuvable`);
      }

      const assignee = this.users.find((user) => user.id === payload.assignee_user_id) ?? null;
      const updatedTicket = {
        ...this.tickets[ticketIndex],
        assignee_user_id: payload.assignee_user_id,
        assignee_name: assignee?.nom ?? null
      };

      this.tickets = [
        ...this.tickets.slice(0, ticketIndex),
        updatedTicket,
        ...this.tickets.slice(ticketIndex + 1)
      ];

      return updatedTicket;
    });
  }

  addTicketComment(ticketId: number, payload: TicketCommentPayload): Observable<TicketComment> {
    if (!this.useMockData) {
      return this.http.post<TicketComment>(`${this.apiBaseUrl}/tickets/${ticketId}/comments`, payload);
    }

    return this.simulateResponse(() => {
      const comment: TicketComment = {
        id: this.ticketComments.length + 1,
        ticket_id: ticketId,
        user_id: payload.user_id ?? null,
        message: payload.message.trim(),
        date_creation: new Date().toISOString()
      };

      this.ticketComments = [comment, ...this.ticketComments];
      return comment;
    });
  }

  getTicketHistory(ticketId: number): Observable<TicketHistory[]> {
    if (!this.useMockData) {
      return this.http.get<TicketHistory[]>(`${this.apiBaseUrl}/tickets/${ticketId}/history`);
    }

    return this.simulateResponse(() => this.ticketHistory.filter((entry) => entry.ticket_id === ticketId));
  }

  getTicketComments(ticketId: number): Observable<TicketComment[]> {
    if (!this.useMockData) {
      return this.http.get<TicketComment[]>(`${this.apiBaseUrl}/tickets/${ticketId}/comments`);
    }

    return this.simulateResponse(() => this.ticketComments.filter((entry) => entry.ticket_id === ticketId));
  }

  getTicketActivity(ticketId: number): Observable<TicketActivity[]> {
    if (!this.useMockData) {
      return this.http.get<TicketActivity[]>(`${this.apiBaseUrl}/tickets/${ticketId}/activity`);
    }

    return this.simulateResponse(() => this.ticketActivity.filter((entry) => entry.ticket_id === ticketId));
  }

  getUsers(): Observable<User[]> {
    if (!this.useMockData) {
      return this.http.get<User[]>(`${this.apiBaseUrl}/users`).pipe(
        catchError(() => this.simulateResponse(() => [...this.users]))
      );
    }

    return this.simulateResponse(() => [...this.users]);
  }

  getUserById(id: number): Observable<User | undefined> {
    if (!this.useMockData) {
      return this.http.get<User>(`${this.apiBaseUrl}/users/${id}`).pipe(map((user) => user ?? undefined));
    }

    return this.simulateResponse(() => this.users.find((user) => user.id === id));
  }

  getProblemGroups(): Observable<ProblemGroup[]> {
    if (!this.useMockData) {
      return this.http.get<ProblemGroup[]>(`${this.apiBaseUrl}/groups`).pipe(
        catchError(() => this.simulateResponse(() => [...this.problemGroups]))
      );
    }

    return this.simulateResponse(() => [...this.problemGroups]);
  }

  getProblemGroupById(id: number): Observable<ProblemGroup | undefined> {
    if (!this.useMockData) {
      return this.http.get<ProblemGroup>(`${this.apiBaseUrl}/groups/${id}`).pipe(map((group) => group ?? undefined));
    }

    return this.simulateResponse(() => this.problemGroups.find((group) => group.id === id));
  }

  getDashboardStats(): Observable<DashboardStats> {
    if (!this.useMockData) {
      return this.http.get<DashboardStats>(`${this.apiBaseUrl}/stats`).pipe(
        catchError(() => this.simulateResponse(() => this.buildStats()))
      );
    }

    return this.simulateResponse(() => this.buildStats());
  }

  getTicketsForUser(userId: number): Observable<Ticket[]> {
    return this.getTickets({}).pipe(map((tickets) => tickets.filter((ticket) => ticket.user_id === userId)));
  }

  getTicketsForDepartment(department: string): Observable<Ticket[]> {
    return this.getTickets({ departement_cible: department });
  }

  private simulateResponse<T>(factory: () => T): Observable<T> {
    return of(factory()).pipe(delay(this.mockLatencyMs));
  }

  private nextId(): number {
    return Math.max(...this.tickets.map((item) => item.id), 0) + 1;
  }

  private applyTicketFilters(tickets: Ticket[], filters: TicketFilters): Ticket[] {
    return tickets.filter((ticket) => {
      const matchesCategorie = !filters.categorie || ticket.categorie === filters.categorie;
      const matchesDepartement = !filters.departement_cible || ticket.departement_cible === filters.departement_cible;
      const matchesGravite = !filters.gravite || ticket.gravite === filters.gravite;
      const matchesPriorite = !filters.priorite || ticket.priorite === filters.priorite;
      const matchesStatut = !filters.statut || ticket.statut === filters.statut;
      return matchesCategorie && matchesDepartement && matchesGravite && matchesPriorite && matchesStatut;
    });
  }

  private buildStats(): DashboardStats {
    const byPriority: Record<TicketPriorite, number> = { faible: 0, normal: 0, urgent: 0 };
    const byDepartment: Record<string, number> = {};
    const byCategory: Record<string, number> = {};

    let ouverts = 0;
    let enCours = 0;
    let resolus = 0;

    for (const ticket of this.tickets) {
      byPriority[ticket.priorite] += 1;
      byDepartment[ticket.departement_cible ?? 'Non défini'] = (byDepartment[ticket.departement_cible ?? 'Non défini'] ?? 0) + 1;
      byCategory[ticket.categorie ?? 'Non défini'] = (byCategory[ticket.categorie ?? 'Non défini'] ?? 0) + 1;

      if (ticket.statut === 'ouvert') {
        ouverts += 1;
      } else if (ticket.statut === 'en_cours') {
        enCours += 1;
      } else {
        resolus += 1;
      }
    }

    return {
      totalTickets: this.tickets.length,
      ouverts,
      enCours,
      resolus,
      byPriority,
      byDepartment,
      byCategory
    };
  }

  private deriveGroupId(payload: TicketCreatePayload): number | null {
    const text = `${payload.titre} ${payload.description} ${payload.categorie}`.toLowerCase();

    if (/(connexion|access|sso|login)/.test(text)) {
      return 1;
    }

    if (/(factur|invoice|paiement|billing)/.test(text)) {
      return 2;
    }

    if (/(rapport|report|export|csv)/.test(text)) {
      return 3;
    }

    return null;
  }

  private deriveAssigneeUserId(payload: TicketCreatePayload): number | null {
    const department = payload.departement_cible.toLowerCase();

    if (department.includes('it')) {
      return 10;
    }

    if (department.includes('finance')) {
      return 11;
    }

    if (department.includes('rh')) {
      return 13;
    }

    if (department.includes('produit')) {
      return 6;
    }

    if (department.includes('achats')) {
      return 8;
    }

    return null;
  }

  private deriveAssigneeName(payload: TicketCreatePayload): string | null {
    const assigneeId = this.deriveAssigneeUserId(payload);
    return this.users.find((user) => user.id === assigneeId)?.nom ?? null;
  }

  private resolveReporterName(userId: number | null): string | null {
    return this.users.find((user) => user.id === userId)?.nom ?? null;
  }

  private resolveReporterEmail(userId: number | null): string | null {
    return this.users.find((user) => user.id === userId)?.email ?? null;
  }

  private toHttpParams(filters: TicketFilters): Record<string, string> {
    return Object.fromEntries(
      Object.entries(filters)
        .filter(([, value]) => Boolean(value))
        .map(([key, value]) => [key, String(value)])
    );
  }
}