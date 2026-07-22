import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Ticket, TicketComment, TicketHistory, TicketStatut, User } from '../../models/item';

@Component({
  selector: 'app-item-detail-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './item-detail-page.component.html',
  styleUrl: './item-detail-page.component.css'
})
export class ItemDetailPageComponent implements OnInit {
  protected ticket: Ticket | null = null;
  protected loading = true;
  protected notFound = false;
  protected selectedStatus: TicketStatut = 'ouvert';
  protected selectedAssigneeId: number | null = null;
  protected commentMessage = '';
  protected updateMessage = '';
  protected users: User[] = [];
  protected history: TicketHistory[] = [];
  protected comments: TicketComment[] = [];

  constructor(
    private readonly route: ActivatedRoute,
    private readonly apiService: ApiService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    if (Number.isNaN(id)) {
      this.notFound = true;
      this.loading = false;
      return;
    }

    this.apiService.getTicketById(id).subscribe({
      next: (ticket) => {
        this.ticket = ticket ?? null;
        this.notFound = !ticket;
        this.selectedStatus = ticket?.statut ?? 'ouvert';
        this.selectedAssigneeId = ticket?.assignee_user_id ?? null;
        this.loading = false;

        if (ticket) {
          this.loadRelations(ticket.id);
        }
      },
      error: () => {
        this.notFound = true;
        this.loading = false;
      }
    });

    this.apiService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
      }
    });
  }

  protected saveStatus(): void {
    if (!this.ticket) {
      return;
    }

    this.apiService.updateTicketStatus(this.ticket.id, { statut: this.selectedStatus }).subscribe({
      next: (updatedTicket) => {
        this.ticket = updatedTicket;
        this.updateMessage = `Statut mis à jour: ${this.formatStatus(updatedTicket.statut)}.`;
      },
      error: () => {
        this.updateMessage = 'Impossible de mettre à jour le statut.';
      }
    });
  }

  protected saveAssignment(): void {
    if (!this.ticket || this.selectedAssigneeId === null) {
      return;
    }

    this.apiService.updateTicketAssignment(this.ticket.id, { assignee_user_id: this.selectedAssigneeId }).subscribe({
      next: (updatedTicket) => {
        this.ticket = updatedTicket;
        this.updateMessage = `Ticket affecté à ${updatedTicket.assignee_name ?? 'non affecté'}.`;
      }
    });
  }

  protected addComment(): void {
    if (!this.ticket || !this.commentMessage.trim()) {
      return;
    }

    this.apiService.addTicketComment(this.ticket.id, { message: this.commentMessage, user_id: this.selectedAssigneeId ?? undefined }).subscribe({
      next: () => {
        this.commentMessage = '';
        this.loadRelations(this.ticket!.id);
      }
    });
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

  protected userLabel(userId: number | null): string {
    return this.users.find((user) => user.id === userId)?.nom ?? 'Non affecté';
  }

  private loadRelations(ticketId: number): void {
    this.apiService.getTicketHistory(ticketId).subscribe({
      next: (history) => {
        this.history = history;
      }
    });

    this.apiService.getTicketComments(ticketId).subscribe({
      next: (comments) => {
        this.comments = comments;
      }
    });
  }
}