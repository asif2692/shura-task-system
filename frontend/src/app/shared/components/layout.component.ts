import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="d-flex" style="min-height:100vh">
      <!-- Sidebar -->
      <nav class="bg-dark text-white p-3" style="width:240px;min-height:100vh">
        <div class="fw-bold mb-4" style="color:#5dade2">Shura Tasks</div>
        <ul class="nav flex-column gap-1">
          <li class="nav-item">
            <a class="nav-link text-white-50" routerLink="/dashboard" routerLinkActive="active text-white">Dashboard</a>
          </li>
          <li class="nav-item">
            <a class="nav-link text-white-50" routerLink="/tasks" routerLinkActive="active text-white">Tasks</a>
          </li>
          <li class="nav-item" *ngIf="canManage">
            <a class="nav-link text-white-50" routerLink="/tasks/create" routerLinkActive="active text-white">Create Task</a>
          </li>
          <li class="nav-item">
            <a class="nav-link text-white-50" routerLink="/events" routerLinkActive="active text-white">Events</a>
          </li>
          <li class="nav-item" *ngIf="canManage">
            <a class="nav-link text-white-50" routerLink="/reports" routerLinkActive="active text-white">Reports</a>
          </li>
          <li class="nav-item">
            <a class="nav-link text-white-50" routerLink="/notifications" routerLinkActive="active text-white">
              Notifications
              <span *ngIf="unread > 0" class="badge bg-danger ms-1">{{ unread }}</span>
            </a>
          </li>
          <li class="nav-item" *ngIf="isAdmin">
            <a class="nav-link text-white-50" routerLink="/users" routerLinkActive="active text-white">Users</a>
          </li>
          <li class="nav-item" *ngIf="isAdmin">
            <a class="nav-link text-white-50" routerLink="/audit-logs" routerLinkActive="active text-white">Audit Logs</a>
          </li>
        </ul>
        <hr class="border-secondary" />
        <div class="small text-white-50 mb-1">{{ userName }}</div>
        <div class="small text-white-50 mb-2">{{ userRole }}</div>
        <button class="btn btn-sm btn-outline-light w-100" (click)="logout()">Logout</button>
      </nav>

      <!-- Main -->
      <main class="flex-grow-1 bg-light overflow-auto">
        <router-outlet />
      </main>
    </div>
  `,
  styles: [`
    .nav-link.active { background: rgba(255,255,255,0.1); border-radius: 6px; }
    .nav-link:hover { color: #fff !important; }
  `],
})
export class LayoutComponent implements OnInit {
  userName = '';
  userRole = '';
  canManage = false;
  isAdmin = false;
  unread = 0;

  constructor(private auth: AuthService, private api: ApiService) {}

  ngOnInit() {
    const u = this.auth.currentUser();
    this.userName = u?.full_name || '';
    this.userRole = u?.role || '';
    this.canManage = this.auth.hasRole('admin', 'shura_member', 'assistant');
    this.isAdmin = this.auth.hasRole('admin');
    this.api.getUnreadCount().subscribe({ next: (r) => (this.unread = r.count) });
  }

  logout() {
    this.auth.logout();
  }
}
