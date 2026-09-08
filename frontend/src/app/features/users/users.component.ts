import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container-fluid py-3">
      <h4 class="mb-3">Users</h4>
      <div class="table-responsive">
        <table class="table table-hover bg-white shadow-sm">
          <thead class="table-light">
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Phone</th><th>Active</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let u of users">
              <td>{{ u.id }}</td>
              <td>{{ u.full_name }}</td>
              <td>{{ u.email }}</td>
              <td><span class="badge bg-secondary">{{ u.role }}</span></td>
              <td>{{ u.phone || '—' }}</td>
              <td>{{ u.is_active ? 'Yes' : 'No' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
})
export class UsersComponent implements OnInit {
  users: any[] = [];
  constructor(private api: ApiService) {}
  ngOnInit() {
    this.api.getUsers().subscribe((u) => (this.users = u));
  }
}
