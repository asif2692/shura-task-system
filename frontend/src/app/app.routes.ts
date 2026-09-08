import { Routes } from '@angular/router';
import { authGuard, roleGuard } from './core/guards/auth.guard';
import { LoginComponent } from './features/auth/login.component';
import { LayoutComponent } from './shared/components/layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { TaskListComponent } from './features/tasks/task-list/task-list.component';
import { TaskCreateComponent } from './features/tasks/task-create/task-create.component';
import { TaskDetailsComponent } from './features/tasks/task-details/task-details.component';
import { EventsComponent } from './features/events/events.component';
import { ReportsComponent } from './features/reports/reports.component';
import { NotificationsComponent } from './features/notifications/notifications.component';
import { UsersComponent } from './features/users/users.component';
import { AuditLogsComponent } from './features/audit-logs/audit-logs.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'tasks', component: TaskListComponent },
      {
        path: 'tasks/create',
        component: TaskCreateComponent,
        canActivate: [roleGuard('admin', 'shura_member', 'assistant')],
      },
      { path: 'tasks/:id', component: TaskDetailsComponent },
      { path: 'events', component: EventsComponent },
      {
        path: 'reports',
        component: ReportsComponent,
        canActivate: [roleGuard('admin', 'shura_member', 'assistant')],
      },
      { path: 'notifications', component: NotificationsComponent },
      {
        path: 'users',
        component: UsersComponent,
        canActivate: [roleGuard('admin')],
      },
      {
        path: 'audit-logs',
        component: AuditLogsComponent,
        canActivate: [roleGuard('admin')],
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
