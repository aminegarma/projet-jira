import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { DashboardStats, Ticket, TicketPriorite, TicketStatut, User } from '../../models/item';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.css'
})
export class DashboardPageComponent implements OnInit {
  protected tickets: Ticket[] = [];
  protected filteredTickets: Ticket[] = [];
  protected users: User[] = [];
  protected stats: DashboardStats | null = null;
  protected categories: string[] = [];
  protected departments: string[] = [];
  protected loading = true;

  protected selectedCategory = 'all';
  protected selectedDepartment = 'all';
  protected selectedGravite = 'all';
  protected selectedPriorite = 'all';
  protected selectedStatut = 'all';
  protected sortBy: 'priorite' | 'date_creation' = 'priorite';
  protected sortDirection: 'asc' | 'desc' = 'desc';

  private readonly priorityRank: Record<TicketPriorite, number> = {
    urgent: 3,
    normal: 2,
    faible: 1
  };

  constructor(private readonly apiService: ApiService) {}

  ngOnInit(): void {
    this.refreshItems();
  }

  protected refreshItems(): void {
    this.loading = true;

    this.apiService.getTickets().subscribe({
      next: (tickets) => {
        this.tickets = tickets;
        this.categories = [...new Set(tickets.map((ticket) => ticket.categorie ?? 'Non défini'))].sort();
        this.departments = [...new Set(tickets.map((ticket) => ticket.departement_cible ?? 'Non défini'))].sort();
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.tickets = [];
        this.filteredTickets = [];
        this.loading = false;
      }
    });

    this.apiService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
      }
    });

    this.apiService.getDashboardStats().subscribe({
      next: (stats) => {
        this.stats = stats;
      }
    });
  }

  protected applyFilters(): void {
    const category = this.selectedCategory;
    const department = this.selectedDepartment;
    const gravite = this.selectedGravite;
    const priorite = this.selectedPriorite;
    const statut = this.selectedStatut;

    const tickets = this.tickets.filter((ticket) => {
      const matchesCategory = category === 'all' || ticket.categorie === category;
      const matchesDepartment = department === 'all' || ticket.departement_cible === department;
      const matchesGravite = gravite === 'all' || ticket.gravite === gravite;
      const matchesPriorite = priorite === 'all' || ticket.priorite === priorite;
      const matchesStatut = statut === 'all' || ticket.statut === statut;
      return matchesCategory && matchesDepartment && matchesGravite && matchesPriorite && matchesStatut;
    });

    this.filteredTickets = [...tickets].sort((left, right) => this.compareTickets(left, right));
  }

  protected resetFilters(): void {
    this.selectedCategory = 'all';
    this.selectedDepartment = 'all';
    this.selectedGravite = 'all';
    this.selectedPriorite = 'all';
    this.selectedStatut = 'all';
    this.sortBy = 'priorite';
    this.sortDirection = 'desc';
    this.applyFilters();
  }

  protected priorityBadgeClass(priority: TicketPriorite): string {
    return `priority-${priority}`;
  }

  protected graviteLabel(gravite: Ticket['gravite']): string {
    switch (gravite) {
      case 'haute':
        return 'Haute';
      case 'faible':
        return 'Faible';
      default:
        return 'Moyenne';
    }
  }

  protected formatStatus(status: TicketStatut): string {
    switch (status) {
      case 'en_cours':
        return 'En cours';
      case 'resolu':
        return 'Résolu';
      default:
        return 'Ouvert';
    }
  }

  protected ticketCategory(ticket: Ticket): string {
    return ticket.categorie ?? 'Non défini';
  }

  protected assigneeLabel(ticket: Ticket): string {
    return ticket.assignee_name ?? 'Non affecté';
  }

  private compareTickets(left: Ticket, right: Ticket): number {
    const direction = this.sortDirection === 'asc' ? 1 : -1;

    if (this.sortBy === 'date_creation') {
      return direction * (new Date(left.date_creation).getTime() - new Date(right.date_creation).getTime());
    }

    return direction * (this.priorityRank[left.priorite] - this.priorityRank[right.priorite]);
  }
}