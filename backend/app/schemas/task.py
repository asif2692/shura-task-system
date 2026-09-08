from datetime import datetime, date, time
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import TaskPriority, TaskStatus, DelayReasonCode


# ---------- Task ----------
class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str | None = None
    event_id: int | None = None
    category: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    start_date: date | None = None
    due_date: date | None = None
    due_time: time | None = None
    notes: str | None = None


class TaskCreate(TaskBase):
    helper_ids: list[int] = Field(..., min_length=1)  # multiple assignment


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=500)
    description: str | None = None
    event_id: int | None = None
    category: str | None = None
    priority: TaskPriority | None = None
    start_date: date | None = None
    due_date: date | None = None
    due_time: time | None = None
    notes: str | None = None
    status: TaskStatus | None = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    status: TaskStatus
    priority_set_by: int | None = None
    priority_set_at: datetime | None = None
    previous_priority: TaskPriority | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    assignments: list["TaskAssignmentOut"] = []


# ---------- Assignment ----------
class TaskAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    helper_id: int
    status: TaskStatus
    acknowledged_at: datetime | None = None
    completed_at: datetime | None = None
    completion_note: str | None = None
    verified_at: datetime | None = None
    verified_by: int | None = None
    delay_reason_code: DelayReasonCode | None = None
    delay_reason_detail: str | None = None
    assigned_at: datetime
    updated_at: datetime


class AssignmentStatusUpdate(BaseModel):
    status: TaskStatus
    note: str | None = None
    completion_note: str | None = None
    delay_reason_code: DelayReasonCode | None = None
    delay_reason_detail: str | None = None


class AssignmentVerify(BaseModel):
    note: str | None = None


# ---------- Follow-up ----------
class FollowupCreate(BaseModel):
    assignment_id: int | None = None
    followup_to: int
    response: str | None = None
    delay_reason_code: DelayReasonCode | None = None
    delay_reason_detail: str | None = None
    next_followup_date: date | None = None
    notes: str | None = None


class FollowupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    assignment_id: int | None = None
    followup_by: int
    followup_to: int
    response: str | None = None
    delay_reason_code: DelayReasonCode | None = None
    delay_reason_detail: str | None = None
    next_followup_date: date | None = None
    notes: str | None = None
    created_at: datetime


# ---------- Status History ----------
class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    assignment_id: int | None = None
    old_status: TaskStatus | None = None
    new_status: TaskStatus
    changed_by: int
    note: str | None = None
    created_at: datetime


# rebuild for forward refs
TaskOut.model_rebuild()
