import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { TicketCreatePayload, TicketGravite, TicketPriorite } from '../../models/item';

@Component({
  selector: 'app-add-jira-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './add-jira-page.component.html',
  styleUrl: './add-jira-page.component.css'
})
export class AddJiraPageComponent {
  protected submittedMessage = '';
  protected isSubmitting = false;
  protected categories = ['access', 'facturation', 'bug', 'impression', 'contrat', 'achats', 'payroll', 'rapport', 'integration', 'logistique'];

  private readonly formBuilder = inject(FormBuilder);
  private readonly apiService = inject(ApiService);
  private readonly router = inject(Router);

  protected readonly form = this.formBuilder.nonNullable.group({
    titre: ['', [Validators.required, Validators.minLength(4)]],
    description: ['', [Validators.required, Validators.minLength(20)]],
    categorie: ['access', [Validators.required]],
    gravite: ['moyenne' as TicketGravite, [Validators.required]],
    priorite: ['normal' as TicketPriorite, [Validators.required]],
    departement_cible: ['IT', [Validators.required]]
  });

  protected submit(): void {
    this.submittedMessage = '';

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;

    const payload: TicketCreatePayload = {
      titre: this.form.getRawValue().titre,
      description: this.form.getRawValue().description,
      categorie: this.form.getRawValue().categorie,
      gravite: this.form.getRawValue().gravite,
      priorite: this.form.getRawValue().priorite,
      departement_cible: this.form.getRawValue().departement_cible
    };

    this.apiService.createTicket(payload).subscribe({
      next: (ticket) => {
        this.submittedMessage = `Ticket créé: #${ticket.id} - ${ticket.titre}.`;
        this.form.reset({
          titre: '',
          description: '',
          categorie: 'access',
          gravite: 'moyenne',
          priorite: 'normal',
          departement_cible: 'IT'
        });
        this.isSubmitting = false;
        this.router.navigateByUrl('/');
      },
      error: () => {
        this.submittedMessage = 'Impossible de soumettre la demande pour le moment.';
        this.isSubmitting = false;
      }
    });
  }
}