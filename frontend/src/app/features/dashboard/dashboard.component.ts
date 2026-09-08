import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="container-fluid py-3">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="mb-0">Dashboard</h4>
        <span class="badge bg-secondary">{{ userRole }}</span>
      </div>

      <div *ngIf="loading" class="text-center py-5">Loading...</div>

      <div *ngIf="!loading && stats" class="row g-3 mb-4">
        <div class="col-6 col-md-3" *ngFor="let card of cards">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="fs-3 fw-bold" [style.color]="card.color">{{ card.value }}</div>
              <div class="small text-muted">{{ card.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">Recent Tasks</div>
            <div class="card-body p-0">
              <div *ngIf="recent.length === 0" class="p-3 text-muted small">No tasks yet.</div>
              <table class="table table-hover mb-0 small" *ngIf="recent.length">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Due</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let t of recent" [routerLink]="['/tasks', t.task_id]" style="cursor:pointer">
                    <td>{{ t.title }}</td>
                    <td><span class="badge bg-light text-dark">{{ t.status }}</span></td>
                    <td>
                      <span class="badge" [ngClass]="{
                        'bg-danger': t.priority==='critical',
                        'bg-warning text-dark': t.priority==='high',
                        'bg-info text-dark': t.priority==='medium',
                        'bg-success': t.priority==='low'
                      }">{{ t.priority }}</span>
                    </td>
                    <td>{{ t.due_date || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">Quick Actions</div>
            <div class="list-group list-group-flush">
              <a routerLink="/tasks/create" class="list-group-item list-group-item-action"
                 *ngIf="canCreate">➕ Create Task</a>
              <a routerLink="/tasks" class="list-group-item list-group-item-action">📋 All Tasks</a>
              <a routerLink="/reports" class="list-group-item list-group-item-action"
                 *ngIf="canReport">📊 Reports</a>
              <a routerLink="/events" class="list-group-item list-group-item-action">📅 Events</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  loading = true;
  stats: any = null;
  extra: any = null;
  recent: any[] = [];
  cards: { label: string; value: number; color: string }[] = [];
  userRole = '';
  canCreate = false;
  canReport = false;

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit() {
    const user = this.auth.currentUser();
    this.userRole = user?.role || '';
    this.canCreate = this.auth.hasRole('admin', 'shura_member', 'assistant');
    this.canReport = this.auth.hasRole('admin', 'shura_member', 'assistant');

    this.api.getDashboardStats().subscribe({
      next: (res) => {
        this.stats = res.stats;
        this.extra = res.extra;
        this.buildCards();
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
    this.api.getRecentTasks().subscribe({ next: (r) => (this.recent = r) });
  }

  private buildCards() {
    if (!this.stats) return;
    if (this.userRole === 'helper') {
      this.cards = [
        { label: 'My Tasks', value: this.stats.my_tasks, color: '#1B4F72' },
        { label: 'Pending', value: this.stats.pending, color: '#e67e22' },
        { label: 'In Progress', value: this.stats.in_progress, color: '#3498db' },
        { label: 'Completed', value: this.stats.completed, color: '#27ae60' },
        { label: 'Overdue', value: this.stats.overdue, color: '#e74c3c' },
        { label: 'Waiting', value: this.stats.waiting, color: '#9b59b6' },
      ];
    } else {
      this.cards = [
        { label: 'Total Tasks', value: this.stats.total_tasks, color: '#1B4F72' },
        { label: 'Completed', value: this.stats.completed, color: '#27ae60' },
        { label: 'Pending', value: this.stats.pending, color: '#e67e22' },
        { label: 'In Progress', value: this.stats.in_progress, color: '#3498db' },
        { label: 'Overdue', value: this.stats.overdue, color: '#e74c3c' },
        { label: 'Critical', value: this.stats.critical, color: '#c0392b' },
        { label: 'Follow-ups', value: this.stats.followups_required, color: '#8e44ad' },
      ];
    }
  }
}
