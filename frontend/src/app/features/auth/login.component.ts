import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-page d-flex align-items-center justify-content-center min-vh-100 bg-light">
      <div class="card shadow-sm" style="width: 400px; max-width: 95%;">
        <div class="card-body p-4">
          <h4 class="text-center mb-1 fw-bold" style="color:#1B4F72">Shura Task System</h4>
          <p class="text-center text-muted small mb-4">شورٰی ٹاسک اینڈ فالو اَپ مینجمنٹ</p>

          <div *ngIf="error" class="alert alert-danger py-2 small">{{ error }}</div>

          <form (ngSubmit)="onSubmit()">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" [(ngModel)]="email" name="email" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" [(ngModel)]="password" name="password" required />
            </div>
            <button class="btn btn-primary w-100" [disabled]="loading">
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </form>

          <hr class="my-3" />
          <p class="small text-muted mb-0">Demo accounts (after seed):</p>
          <ul class="small text-muted mb-0">
            <li>admin@shura.local / admin123</li>
            <li>shura@shura.local / shura123</li>
            <li>assistant@shura.local / assistant123</li>
            <li>ahmed@shura.local / helper123</li>
          </ul>
        </div>
      </div>
    </div>
  `,
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error = '';

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit() {
    this.loading = true;
    this.error = '';
    this.auth.login({ email: this.email, password: this.password }).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Login failed';
      },
    });
  }
}
