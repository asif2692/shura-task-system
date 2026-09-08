import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-audit-logs',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container-fluid py-3">
      <h4 class="mb-3">Audit Logs</h4>
      <div class="table-responsive">
        <table class="table table-sm table-hover bg-white shadow-sm">
          <thead class="table-light">
            <tr><th>Time</th><th>User</th><th>Action</th><th>Entity</th><th>Old</th><th>New</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let l of logs">
              <td class="small">{{ l.created_at | date:'medium' }}</td>
              <td>{{ l.user_id }}</td>
              <td><code>{{ l.action }}</code></td>
              <td>{{ l.entity_type }} #{{ l.entity_id }}</td>
              <td class="small text-muted">{{ l.old_value || '—' }}</td>
              <td class="small">{{ l.new_value || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
})
export class AuditLogsComponent implements OnInit {
  logs: any[] = [];
  constructor(private api: ApiService) {}
  ngOnInit() {
    this.api.getAuditLogs().subscribe((l) => (this.logs = l));
  }
}
