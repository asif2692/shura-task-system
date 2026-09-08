import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container-fluid py-3">
      <h4 class="mb-3">Reports</h4>

      <div class="row g-3 mb-4" *ngIf="summary">
        <div class="col-6 col-md-3" *ngFor="let c of summaryCards">
          <div class="card border-0 shadow-sm text-center">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ c.value }}</div>
              <div class="small text-muted">{{ c.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">Helper Performance</div>
            <div class="table-responsive">
              <table class="table table-sm mb-0">
                <thead><tr><th>Name</th><th>Total</th><th>Done</th><th>Overdue</th><th>Rate</th></tr></thead>
                <tbody>
                  <tr *ngFor="let h of performance">
                    <td>{{ h.full_name }}</td>
                    <td>{{ h.total_tasks }}</td>
                    <td>{{ h.completed }}</td>
                    <td>{{ h.overdue }}</td>
                    <td>{{ h.completion_rate }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-semibold">Overdue Tasks</div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item" *ngFor="let t of overdue">
                <strong>{{ t.title }}</strong>
                <span class="badge bg-danger ms-2">{{ t.days_overdue }}d overdue</span>
                <div class="small text-muted">Due: {{ t.due_date }} · {{ t.priority }}</div>
              </li>
              <li class="list-group-item text-muted" *ngIf="overdue.length===0">No overdue tasks</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class ReportsComponent implements OnInit {
  summary: any = null;
  performance: any[] = [];
  overdue: any[] = [];
  summaryCards: { label: string; value: any }[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getReportSummary().subscribe((s) => {
      this.summary = s;
      this.summaryCards = [
        { label: 'Total Tasks', value: s.total_tasks },
        { label: 'Completed', value: s.completed_tasks },
        { label: 'Overdue', value: s.overdue_tasks },
        { label: 'On-Time %', value: s.on_time_completion_pct + '%' },
      ];
    });
    this.api.getHelperPerformance().subscribe((p) => (this.performance = p));
    this.api.getOverdueReport().subscribe((o) => (this.overdue = o));
  }
}
