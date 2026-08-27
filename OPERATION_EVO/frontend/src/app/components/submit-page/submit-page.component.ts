import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Ticket, TicketPriorite } from '../../models/item';

@Component({
  selector: 'app-submit-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './submit-page.component.html',
  styleUrl: './submit-page.component.css'
})
export class SubmitPageComponent {
  protected loadingTickets = true;
  protected tickets: Ticket[] = [];

  private readonly apiService = inject(ApiService);

  constructor() {
    this.refreshTickets();
  }

  protected refreshTickets(): void {
    this.loadingTickets = true;

    this.apiService.getTickets().subscribe({
      next: (tickets) => {
        this.tickets = tickets;
        this.loadingTickets = false;
      },
      error: () => {
        this.tickets = [];
        this.loadingTickets = false;
      }
    });
  }

  protected formatStatus(status: string): string {
    switch (status) {
      case 'en_cours':
        return 'En cours';
      case 'resolu':
        return 'Résolu';
      default:
        return 'Ouvert';
    }
  }

  protected formatPriority(priority: TicketPriorite): string {
    switch (priority) {
      case 'faible':
        return 'Faible';
      case 'urgent':
        return 'Urgente';
      default:
        return 'Normale';
    }
  }

  protected sortedTickets(): Ticket[] {
    return [...this.tickets]
      .sort((left, right) => new Date(right.date_creation).getTime() - new Date(left.date_creation).getTime());
  }
}