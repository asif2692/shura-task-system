import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User } from '../../shared/models/user.model';
import { Task, TaskCreate, TaskAssignment, Followup } from '../../shared/models/task.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ---- Users ----
  getHelpers(groupId?: number): Observable<User[]> {
    let params = new HttpParams();
    if (groupId) params = params.set('group_id', groupId);
    return this.http.get<User[]>(`${this.base}/users/helpers`, { params });
  }

  getUsers(role?: string): Observable<User[]> {
    let params = new HttpParams();
    if (role) params = params.set('role', role);
    return this.http.get<User[]>(`${this.base}/users/`, { params });
  }

  // ---- Tasks ----
  getTasks(filters?: Record<string, string>): Observable<Task[]> {
    let params = new HttpParams();
    if (filters) {
      Object.entries(filters).forEach(([k, v]) => {
        if (v) params = params.set(k, v);
      });
    }
    return this.http.get<Task[]>(`${this.base}/tasks/`, { params });
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.base}/tasks/${id}`);
  }

  createTask(data: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.base}/tasks/`, data);
  }

  updateTask(id: number, data: Partial<Task>): Observable<Task> {
    return this.http.patch<Task>(`${this.base}/tasks/${id}`, data);
  }

  updateAssignmentStatus(assignmentId: number, body: any): Observable<TaskAssignment> {
    return this.http.patch<TaskAssignment>(`${this.base}/tasks/assignments/${assignmentId}/status`, body);
  }

  verifyAssignment(assignmentId: number, note?: string): Observable<TaskAssignment> {
    return this.http.post<TaskAssignment>(`${this.base}/tasks/assignments/${assignmentId}/verify`, { note });
  }

  createFollowup(taskId: number, body: any): Observable<Followup> {
    return this.http.post<Followup>(`${this.base}/tasks/${taskId}/followups`, body);
  }

  getFollowups(taskId: number): Observable<Followup[]> {
    return this.http.get<Followup[]>(`${this.base}/tasks/${taskId}/followups`);
  }

  // ---- Events ----
  getEvents(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/events/`);
  }

  createEvent(data: any): Observable<any> {
    return this.http.post(`${this.base}/events/`, data);
  }

  // ---- Groups ----
  getGroups(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/groups/`);
  }

  getGroupMembers(groupId: number): Observable<User[]> {
    return this.http.get<User[]>(`${this.base}/groups/${groupId}/members`);
  }

  // ---- Dashboard ----
  getDashboardStats(): Observable<any> {
    return this.http.get(`${this.base}/dashboard/stats`);
  }

  getRecentTasks(limit = 10): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/dashboard/recent-tasks`, {
      params: { limit },
    });
  }

  // ---- Notifications ----
  getNotifications(unreadOnly = false): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/notifications/`, {
      params: { unread_only: unreadOnly },
    });
  }

  getUnreadCount(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(`${this.base}/notifications/unread-count`);
  }

  markNotificationRead(id: number): Observable<any> {
    return this.http.patch(`${this.base}/notifications/${id}/read`, {});
  }

  markAllRead(): Observable<void> {
    return this.http.post<void>(`${this.base}/notifications/mark-all-read`, {});
  }

  // ---- Reports ----
  getReportSummary(from?: string, to?: string): Observable<any> {
    let params = new HttpParams();
    if (from) params = params.set('from_date', from);
    if (to) params = params.set('to_date', to);
    return this.http.get(`${this.base}/reports/summary`, { params });
  }

  getHelperPerformance(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/reports/helper-performance`);
  }

  getOverdueReport(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/reports/overdue`);
  }

  getEventReport(eventId: number): Observable<any> {
    return this.http.get(`${this.base}/reports/event-wise/${eventId}`);
  }

  // ---- WhatsApp ----
  getWhatsAppLink(taskId: number, helperId: number): Observable<any> {
    return this.http.get(`${this.base}/whatsapp/task/${taskId}/helper/${helperId}`);
  }

  getWhatsAppLinksForTask(taskId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/whatsapp/task/${taskId}`);
  }

  // ---- Audit ----
  getAuditLogs(params?: Record<string, string>): Observable<any[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v) httpParams = httpParams.set(k, v);
      });
    }
    return this.http.get<any[]>(`${this.base}/audit-logs/`, { params: httpParams });
  }
}
