import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-events',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container-fluid py-3">
      <div class="d-flex justify-content-between mb-3">
        <h4 class="mb-0">Events</h4>
        <button *ngIf="canManage" class="btn btn-primary btn-sm" (click)="showForm = !showForm">
          {{ showForm ? 'Cancel' : '+ New Event' }}
        </button>
      </div>

      <div class="card border-0 shadow-sm mb-3" *ngIf="showForm">
        <div class="card-body">
          <div class="row g-2">
            <div class="col-md-4"><input class="form-control" placeholder="Event Name *" [(ngModel)]="form.name" /></div>
            <div class="col-md-3"><input type="date" class="form-control" [(ngModel)]="form.start_date" /></div>
            <div class="col-md-3"><input type="date" class="form-control" [(ngModel)]="form.end_date" /></div>
            <div class="col-md-2"><button class="btn btn-success w-100" (click)="create()" [disabled]="!form.name">Save</button></div>
            <div class="col-12"><input class="form-control" placeholder="Location" [(ngModel)]="form.location" /></div>
            <div class="col-12"><textarea class="form-control" placeholder="Description" [(ngModel)]="form.description" rows="2"></textarea></div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-4" *ngFor="let e of events">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h6 class="fw-bold">{{ e.name }}</h6>
              <p class="small text-muted mb-1">{{ e.location || '—' }}</p>
              <p class="small mb-0">{{ e.start_date || '' }} → {{ e.end_date || '' }}</p>
            </div>
          </div>
        </div>
      </div>
      <div *ngIf="events.length===0" class="text-muted">No events yet.</div>
    </div>
  `,
})
export class EventsComponent implements OnInit {
  events: any[] = [];
  showForm = false;
  canManage = false;
  form: any = { name: '', description: '', start_date: '', end_date: '', location: '' };

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit() {
    this.canManage = this.auth.hasRole('admin', 'shura_member', 'assistant');
    this.load();
  }

  load() {
    this.api.getEvents().subscribe((e) => (this.events = e));
  }

  create() {
    this.api.createEvent(this.form).subscribe({
      next: () => {
        this.showForm = false;
        this.form = { name: '', description: '', start_date: '', end_date: '', location: '' };
        this.load();
      },
    });
  }
}
