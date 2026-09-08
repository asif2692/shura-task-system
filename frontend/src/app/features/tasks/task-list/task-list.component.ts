import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { Task, STATUS_LABELS } from '../../../shared/models/task.model';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="container-fluid py-3">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h4 class="mb-0">Tasks</h4>
        <a *ngIf="canCreate" routerLink="/tasks/create" class="btn btn-primary btn-sm">+ New Task</a>
      </div>

      <div class="row g-2 mb-3">
        <div class="col-auto">
          <select class="form-select form-select-sm" [(ngModel)]="filterStatus" (change)="load()">
            <option value="">All Status</option>
            <option *ngFor="let s of statuses" [value]="s">{{ statusLabels[s] }}</option>
          </select>
        </div>
        <div class="col-auto">
          <select class="form-select form-select-sm" [(ngModel)]="filterPriority" (change)="load()">
            <option value="">All Priority</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div *ngIf="loading" class="text-center py-4">Loading...</div>
      <div *ngIf="!loading && tasks.length === 0" class="text-muted">No tasks found.</div>

      <div class="table-responsive" *ngIf="!loading && tasks.length">
        <table class="table table-hover align-middle bg-white shadow-sm">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Due</th>
              <th>Helpers</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let t of tasks">
              <td>#{{ t.id }}</td>
              <td>{{ t.title }}</td>
              <td>
                <span class="badge" [ngClass]="{
                  'bg-danger': t.priority==='critical',
                  'bg-warning text-dark': t.priority==='high',
                  'bg-info text-dark': t.priority==='medium',
                  'bg-success': t.priority==='low'
                }">{{ t.priority }}</span>
              </td>
              <td><span class="badge bg-secondary">{{ statusLabels[t.status] }}</span></td>
              <td>{{ t.due_date || '—' }}</td>
              <td>{{ t.assignments?.length || 0 }}</td>
              <td><a [routerLink]="['/tasks', t.id]" class="btn btn-sm btn-outline-primary">View</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
})
export class TaskListComponent implements OnInit {
  tasks: Task[] = [];
  loading = true;
  filterStatus = '';
  filterPriority = '';
  canCreate = false;
  statusLabels = STATUS_LABELS;
  statuses = Object.keys(STATUS_LABELS);

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit() {
    this.canCreate = this.auth.hasRole('admin', 'shura_member', 'assistant');
    this.load();
  }

  load() {
    this.loading = true;
    const filters: Record<string, string> = {};
    if (this.filterStatus) filters['status'] = this.filterStatus;
    if (this.filterPriority) filters['priority'] = this.filterPriority;
    this.api.getTasks(filters).subscribe({
      next: (t) => {
        this.tasks = t;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
