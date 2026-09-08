import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container-fluid py-3">
      <div class="d-flex justify-content-between mb-3">
        <h4 class="mb-0">Notifications</h4>
        <button class="btn btn-sm btn-outline-secondary" (click)="markAll()" *ngIf="items.length">Mark all read</button>
      </div>
      <div class="list-group shadow-sm">
        <div *ngFor="let n of items"
             class="list-group-item list-group-item-action"
             [class.bg-light]="!n.is_read"
             (click)="markRead(n)">
          <div class="d-flex justify-content-between">
            <strong>{{ n.title }}</strong>
            <small class="text-muted">{{ n.created_at | date:'short' }}</small>
          </div>
          <div class="small">{{ n.message }}</div>
        </div>
        <div *ngIf="items.length===0" class="list-group-item text-muted">No notifications</div>
      </div>
    </div>
  `,
})
export class NotificationsComponent implements OnInit {
  items: any[] = [];
  constructor(private api: ApiService) {}
  ngOnInit() {
    this.api.getNotifications().subscribe((n) => (this.items = n));
  }
  markRead(n: any) {
    if (n.is_read) return;
    this.api.markNotificationRead(n.id).subscribe(() => (n.is_read = true));
  }
  markAll() {
    this.api.markAllRead().subscribe(() => this.items.forEach((i) => (i.is_read = true)));
  }
}
