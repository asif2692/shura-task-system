export type TaskPriority = 'critical' | 'high' | 'medium' | 'low';
export type TaskStatus =
  | 'new'
  | 'assigned'
  | 'acknowledged'
  | 'in_progress'
  | 'waiting'
  | 'followup_required'
  | 'overdue'
  | 'completed'
  | 'verified'
  | 'cancelled';

export interface TaskAssignment {
  id: number;
  task_id: number;
  helper_id: number;
  status: TaskStatus;
  acknowledged_at?: string | null;
  completed_at?: string | null;
  completion_note?: string | null;
  verified_at?: string | null;
  verified_by?: number | null;
  delay_reason_code?: string | null;
  delay_reason_detail?: string | null;
  assigned_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  created_by: number;
  event_id?: number | null;
  category?: string | null;
  priority: TaskPriority;
  priority_set_by?: number | null;
  priority_set_at?: string | null;
  previous_priority?: TaskPriority | null;
  start_date?: string | null;
  due_date?: string | null;
  due_time?: string | null;
  status: TaskStatus;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  assignments: TaskAssignment[];
}

export interface TaskCreate {
  title: string;
  description?: string;
  event_id?: number;
  category?: string;
  priority?: TaskPriority;
  start_date?: string;
  due_date?: string;
  due_time?: string;
  notes?: string;
  helper_ids: number[];
}

export interface Followup {
  id: number;
  task_id: number;
  assignment_id?: number | null;
  followup_by: number;
  followup_to: number;
  response?: string | null;
  delay_reason_code?: string | null;
  delay_reason_detail?: string | null;
  next_followup_date?: string | null;
  notes?: string | null;
  created_at: string;
}

export const PRIORITY_COLORS: Record<TaskPriority, string> = {
  critical: '#e74c3c',
  high: '#e67e22',
  medium: '#f1c40f',
  low: '#2ecc71',
};

export const STATUS_LABELS: Record<TaskStatus, string> = {
  new: 'New',
  assigned: 'Assigned',
  acknowledged: 'Acknowledged',
  in_progress: 'In Progress',
  waiting: 'Waiting',
  followup_required: 'Follow-up Required',
  overdue: 'Overdue',
  completed: 'Completed',
  verified: 'Verified',
  cancelled: 'Cancelled',
};
