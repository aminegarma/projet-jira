export type TicketGravite = 'faible' | 'moyenne' | 'haute';

export type TicketPriorite = 'faible' | 'normal' | 'urgent';

export type TicketStatut = 'ouvert' | 'en_cours' | 'resolu';

export interface User {
  id: number;
  nom: string;
  email: string;
  poste: string | null;
  departement: string | null;
  role: string | null;
  date_creation: string;
}

export interface ProblemGroup {
  id: number;
  titre_probleme: string;
  ticket_maitre_id: number | null;
  statut: 'ouvert' | 'en_cours' | 'resolu';
  date_creation: string;
}

export interface TicketHistory {
  id: number;
  ticket_id: number;
  action: string;
  date_action: string;
}

export interface TicketComment {
  id: number;
  ticket_id: number;
  user_id: number | null;
  message: string;
  date_creation: string;
}

export interface TicketActivity {
  id: number;
  ticket_id: number;
  action: string;
  details: string | null;
  created_at: string;
}

export interface Ticket {
  id: number;
  titre: string;
  description: string | null;
  categorie: string | null;
  gravite: TicketGravite;
  priorite: TicketPriorite;
  departement_cible: string | null;
  statut: TicketStatut;
  date_creation: string;
  user_id: number | null;
  groupe_id: number | null;
  assignee_user_id: number | null;
  assignee_name?: string | null;
  reporter_name?: string | null;
  reporter_email?: string | null;
}

export interface TicketCreatePayload {
  titre: string;
  description: string;
  categorie: string;
  gravite: TicketGravite;
  priorite: TicketPriorite;
  departement_cible: string;
  user_id?: number | null;
}

export interface TicketUpdateStatusPayload {
  statut: TicketStatut;
}

export interface TicketAssignPayload {
  assignee_user_id: number;
}

export interface TicketCommentPayload {
  user_id?: number | null;
  message: string;
}

export interface TicketFilters {
  categorie?: string;
  departement_cible?: string;
  gravite?: string;
  priorite?: string;
  statut?: string;
}

export interface DashboardStats {
  totalTickets: number;
  ouverts: number;
  enCours: number;
  resolus: number;
  byPriority: Record<TicketPriorite, number>;
  byDepartment: Record<string, number>;
  byCategory: Record<string, number>;
}

export interface Item extends Ticket {}
export interface CreateItemPayload extends TicketCreatePayload {}
export interface ItemFilters extends TicketFilters {}
export interface ItemStatusUpdatePayload extends TicketUpdateStatusPayload {}