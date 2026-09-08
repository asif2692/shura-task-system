import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { Task, STATUS_LABELS, TaskStatus } from '../../../shared/models/task.model';

@Component({
  selector: 'app-task-details',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="container-fluid py-3" *ngIf="task">
      <a routerLink="/tasks" class="small text-decoration-none">← Back to Tasks</a>
      <div class="d-flex justify-content-between align-items-start mt-2 mb-3 flex-wrap gap-2">
        <div>
          <h4 class="mb-1">{{ task.title }}</h4>
          <span class="badge me-1" [ngClass]="{
            'bg-danger': task.priority==='critical',
            'bg-warning text-dark': task.priority==='high',
            'bg-info text-dark': task.priority==='medium',
            'bg-success': task.priority==='low'
          }">{{ task.priority }}</span>
          <span class="badge bg-secondary">{{ statusLabels[task.status] }}</span>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm mb-3">
            <div class="card-body">
              <p class="mb-2" *ngIf="task.description">{{ task.description }}</p>
              <div class="row small text-muted">
                <div class="col-sm-4"><strong>Due:</strong> {{ task.due_date || '—' }} {{ task.due_time || '' }}</div>
                <div class="col-sm-4"><strong>Created:</strong> {{ task.created_at | date:'medium' }}</div>
                <div class="col-sm-4"><strong>Category:</strong> {{ task.category || '—' }}</div>
              </div>
              <p class="mt-2 mb-0 small" *ngIf="task.notes"><strong>Notes:</strong> {{ task.notes }}</p>
            </div>
          </div>

          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">Assignments ({{ task.assignments?.length || 0 }})</div>
            <div class="table-responsive">
              <table class="table table-sm mb-0 align-middle">
                <thead>
                  <tr>
                    <th>Helper ID</th>
                    <th>Status</th>
                    <th>Acknowledged</th>
                    <th>Completed</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let a of task.assignments">
                    <td>#{{ a.helper_id }}</td>
                    <td><span class="badge bg-light text-dark">{{ statusLabels[a.status] }}</span></td>
                    <td class="small">{{ a.acknowledged_at ? (a.acknowledged_at | date:'short') : '—' }}</td>
                    <td class="small">{{ a.completed_at ? (a.completed_at | date:'short') : '—' }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <!-- Helper actions -->
                        <button *ngIf="isOwn(a) && a.status==='assigned'"
                                class="btn btn-outline-primary" (click)="setStatus(a.id, 'acknowledged')">
                          Acknowledge
                        </button>
                        <button *ngIf="isOwn(a) && (a.status==='acknowledged' || a.status==='assigned')"
                                class="btn btn-outline-info" (click)="setStatus(a.id, 'in_progress')">
                          Start
                        </button>
                        <button *ngIf="isOwn(a) && a.status==='in_progress'"
                                class="btn btn-outline-success" (click)="setStatus(a.id, 'completed')">
                          Complete
                        </button>
                        <!-- Verify -->
                        <button *ngIf="canManage && a.status==='completed'"
                                class="btn btn-success" (click)="verify(a.id)">
                          Verify
                        </button>
                        <!-- WhatsApp -->
                        <button *ngIf="canManage" class="btn btn-outline-success"
                                (click)="openWhatsApp(a.helper_id)" title="WhatsApp">
                          📱
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Follow-ups -->
          <div class="card border-0 shadow-sm mt-3" *ngIf="canManage">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <span class="fw-semibold">Follow-ups</span>
            </div>
            <div class="card-body">
              <div *ngFor="let f of followups" class="border-bottom pb-2 mb-2 small">
                <div class="text-muted">{{ f.created_at | date:'medium' }} — by #{{ f.followup_by }} → #{{ f.followup_to }}</div>
                <div *ngIf="f.notes">{{ f.notes }}</div>
                <div *ngIf="f.response"><em>Response: {{ f.response }}</em></div>
              </div>
              <div *ngIf="followups.length===0" class="text-muted small mb-2">No follow-ups yet.</div>
              <div class="row g-2">
                <div class="col-md-4">
                  <select class="form-select form-select-sm" [(ngModel)]="fuTo">
                    <option [ngValue]="null">Select helper...</option>
                    <option *ngFor="let a of task.assignments" [ngValue]="a.helper_id">Helper #{{ a.helper_id }}</option>
                  </select>
                </div>
                <div class="col-md-5">
                  <input class="form-control form-control-sm" placeholder="Notes" [(ngModel)]="fuNotes" />
                </div>
                <div class="col-md-3">
                  <button class="btn btn-sm btn-primary w-100" [disabled]="!fuTo" (click)="addFollowup()">Add Follow-up</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">WhatsApp (all helpers)</div>
            <div class="list-group list-group-flush">
              <button *ngFor="let a of task.assignments" class="list-group-item list-group-item-action"
                      (click)="openWhatsApp(a.helper_id)">
                📱 Helper #{{ a.helper_id }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div *ngIf="!task && !loading" class="container py-5 text-muted">Task not found.</div>
  `,
})
export class TaskDetailsComponent implements OnInit {
  task: Task | null = null;
  followups: any[] = [];
  loading = true;
  statusLabels = STATUS_LABELS;
  canManage = false;
  fuTo: number | null = null;
  fuNotes = '';

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.canManage = this.auth.hasRole('admin', 'shura_member', 'assistant');
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.load(id);
  }

  load(id: number) {
    this.api.getTask(id).subscribe({
      next: (t) => {
        this.task = t;
        this.loading = false;
        this.api.getFollowups(id).subscribe((f) => (this.followups = f));
      },
      error: () => (this.loading = false),
    });
  }

  isOwn(a: any): boolean {
    return this.auth.currentUser()?.id === a.helper_id;
  }

  setStatus(assignmentId: number, status: string) {
    this.api.updateAssignmentStatus(assignmentId, { status }).subscribe({
      next: () => this.load(this.task!.id),
    });
  }

  verify(assignmentId: number) {
    this.api.verifyAssignment(assignmentId).subscribe({
      next: () => this.load(this.task!.id),
    });
  }

  openWhatsApp(helperId: number) {
    if (!this.task) return;
    this.api.getWhatsAppLink(this.task.id, helperId).subscribe({
      next: (res) => {
        if (res.wa_url) {
          window.open(res.wa_url, '_blank');
        } else {
          alert('No phone number for this helper.\n\nMessage:\n' + res.message);
        }
      },
    });
  }

  addFollowup() {
    if (!this.task || !this.fuTo) return;
    this.api
      .createFollowup(this.task.id, {
        followup_to: this.fuTo,
        notes: this.fuNotes,
      })
      .subscribe({
        next: () => {
          this.fuNotes = '';
          this.fuTo = null;
          this.api.getFollowups(this.task!.id).subscribe((f) => (this.followups = f));
        },
      });
  }
}
