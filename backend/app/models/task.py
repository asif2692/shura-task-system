from datetime import datetime, date, time, timezone
from sqlalchemy import (
    String, Text, DateTime, Date, Time, Boolean, ForeignKey,
    Enum as SAEnum, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import TaskPriority, TaskStatus, DelayReasonCode


class Task(Base):
    """Master Task – one record even if assigned to many helpers."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, native_enum=False), default=TaskPriority.MEDIUM, index=True
    )
    priority_set_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    priority_set_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    previous_priority: Mapped[TaskPriority | None] = mapped_column(SAEnum(TaskPriority, native_enum=False), nullable=True)

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    due_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # Overall status (derived / highest priority among assignments)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, native_enum=False), default=TaskStatus.NEW, index=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    created_by_user = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    event = relationship("Event", back_populates="tasks")
    assignments = relationship(
        "TaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )
    status_history = relationship(
        "TaskStatusHistory", back_populates="task", cascade="all, delete-orphan"
    )
    followups = relationship(
        "TaskFollowup", back_populates="task", cascade="all, delete-orphan"
    )
    attachments = relationship(
        "Attachment", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title[:40]}>"


class TaskAssignment(Base):
    """Individual assignment of a Master Task to one Helper."""
    __tablename__ = "task_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    helper_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, native_enum=False), default=TaskStatus.ASSIGNED, index=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Completion
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Delay
    delay_reason_code: Mapped[DelayReasonCode | None] = mapped_column(
        SAEnum(DelayReasonCode, native_enum=False), nullable=True
    )
    delay_reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    task = relationship("Task", back_populates="assignments")
    helper = relationship("User", back_populates="assignments", foreign_keys=[helper_id])
    verifier = relationship("User", foreign_keys=[verified_by])
    status_history = relationship(
        "TaskStatusHistory", back_populates="assignment", cascade="all, delete-orphan"
    )
    followups = relationship(
        "TaskFollowup", back_populates="assignment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TaskAssignment task={self.task_id} helper={self.helper_id} status={self.status}>"


class TaskStatusHistory(Base):
    __tablename__ = "task_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_assignments.id"), nullable=True, index=True
    )
    old_status: Mapped[TaskStatus | None] = mapped_column(SAEnum(TaskStatus, native_enum=False), nullable=True)
    new_status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus, native_enum=False), nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    task = relationship("Task", back_populates="status_history")
    assignment = relationship("TaskAssignment", back_populates="status_history")
    changed_by_user = relationship("User", foreign_keys=[changed_by])


class TaskFollowup(Base):
    __tablename__ = "task_followups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_assignments.id"), nullable=True, index=True
    )

    followup_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    followup_to: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    delay_reason_code: Mapped[DelayReasonCode | None] = mapped_column(
        SAEnum(DelayReasonCode, native_enum=False), nullable=True
    )
    delay_reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_followup_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    task = relationship("Task", back_populates="followups")
    assignment = relationship("TaskAssignment", back_populates="followups")
    followup_by_user = relationship("User", foreign_keys=[followup_by])
    followup_to_user = relationship("User", foreign_keys=[followup_to])


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_assignments.id"), nullable=True
    )
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)  # Supabase Storage path
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])
