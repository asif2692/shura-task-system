import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../../core/services/api.service';
import { User } from '../../../shared/models/user.model';
import { TaskCreate } from '../../../shared/models/task.model';

@Component({
  selector: 'app-task-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container py-3" style="max-width:720px">
      <h4 class="mb-3">Create Task</h4>
      <div *ngIf="error" class="alert alert-danger">{{ error }}</div>
      <div *ngIf="success" class="alert alert-success">Task created successfully!</div>

      <form (ngSubmit)="submit()" class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Title *</label>
            <input class="form-control" [(ngModel)]="form.title" name="title" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea class="form-control" rows="3" [(ngModel)]="form.description" name="description"></textarea>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-md-4">
              <label class="form-label">Priority</label>
              <select class="form-select" [(ngModel)]="form.priority" name="priority">
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Due Date</label>
              <input type="date" class="form-control" [(ngModel)]="form.due_date" name="due_date" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Due Time</label>
              <input type="time" class="form-control" [(ngModel)]="form.due_time" name="due_time" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Event</label>
            <select class="form-select" [(ngModel)]="form.event_id" name="event_id">
              <option [ngValue]="undefined">— None —</option>
              <option *ngFor="let e of events" [ngValue]="e.id">{{ e.name }}</option>
            </select>
          </div>

          <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <label class="form-label mb-0">Assign Helpers *</label>
              <div>
                <button type="button" class="btn btn-sm btn-outline-secondary me-1" (click)="selectAll()">Select All</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" (click)="deselectAll()">Deselect</button>
              </div>
            </div>
            <div class="border rounded p-2" style="max-height:200px;overflow:auto">
              <div class="form-check" *ngFor="let h of helpers">
                <input class="form-check-input" type="checkbox"
                       [id]="'h'+h.id" [checked]="selected.has(h.id)"
                       (change)="toggle(h.id)" />
                <label class="form-check-label" [for]="'h'+h.id">
                  {{ h.full_name }} <span class="text-muted small" *ngIf="h.phone">({{ h.phone }})</span>
                </label>
              </div>
              <div *ngIf="helpers.length===0" class="text-muted small">No helpers found. Create helpers first.</div>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label">Notes</label>
            <textarea class="form-control" rows="2" [(ngModel)]="form.notes" name="notes"></textarea>
          </div>

          <button class="btn btn-primary" [disabled]="loading || !form.title || selected.size===0">
            {{ loading ? 'Creating...' : 'Create & Assign' }}
          </button>
          <button type="button" class="btn btn-link" (click)="router.navigate(['/tasks'])">Cancel</button>
        </div>
      </form>
    </div>
  `,
})
export class TaskCreateComponent implements OnInit {
  form: TaskCreate = {
    title: '',
    description: '',
    priority: 'medium',
    helper_ids: [],
  };
  helpers: User[] = [];
  events: any[] = [];
  selected = new Set<number>();
  loading = false;
  error = '';
  success = false;

  constructor(private api: ApiService, public router: Router) {}

  ngOnInit() {
    this.api.getHelpers().subscribe((h) => (this.helpers = h));
    this.api.getEvents().subscribe((e) => (this.events = e));
  }

  toggle(id: number) {
    if (this.selected.has(id)) this.selected.delete(id);
    else this.selected.add(id);
  }

  selectAll() {
    this.helpers.forEach((h) => this.selected.add(h.id));
  }

  deselectAll() {
    this.selected.clear();
  }

  submit() {
    this.loading = true;
    this.error = '';
    this.form.helper_ids = Array.from(this.selected);
    this.api.createTask(this.form).subscribe({
      next: (task) => {
        this.loading = false;
        this.success = true;
        setTimeout(() => this.router.navigate(['/tasks', task.id]), 800);
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Failed to create task';
      },
    });
  }
}
