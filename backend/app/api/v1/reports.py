from datetime import date, datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.models.task import Task, TaskAssignment, TaskFollowup
from app.models.event import Event
from app.models.enums import UserRole, TaskStatus, TaskPriority

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
async def report_summary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    q = select(Task).where(Task.is_active == True)
    if from_date:
        q = q.where(Task.created_at >= datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc))
    if to_date:
        q = q.where(Task.created_at <= datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc))

    result = await db.execute(q)
    tasks = result.scalars().all()

    assign_q = select(TaskAssignment)
    assign_result = await db.execute(assign_q)
    assignments = assign_result.scalars().all()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED))
    overdue = sum(
        1 for t in tasks
        if t.due_date and t.due_date < date.today()
        and t.status not in (TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CANCELLED)
    )
    on_time = 0
    completion_times = []
    for a in assignments:
        if a.completed_at and a.assigned_at:
            days = (a.completed_at - a.assigned_at).total_seconds() / 86400
            completion_times.append(days)
            # check against task due
            # simplified on-time: completed before or on due
    avg_completion = round(sum(completion_times) / len(completion_times), 2) if completion_times else None

    by_priority = {}
    for p in TaskPriority:
        by_priority[p.value] = sum(1 for t in tasks if t.priority == p)

    by_status = {}
    for s in TaskStatus:
        by_status[s.value] = sum(1 for t in tasks if t.status == s)

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "overdue_tasks": overdue,
        "on_time_completion_pct": round((completed / total * 100), 1) if total else 0,
        "average_completion_days": avg_completion,
        "by_priority": by_priority,
        "by_status": by_status,
        "total_assignments": len(assignments),
        "period": {"from": from_date.isoformat() if from_date else None, "to": to_date.isoformat() if to_date else None},
    }


@router.get("/helper-performance")
async def helper_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    helpers_result = await db.execute(
        select(User).where(User.role == UserRole.HELPER, User.is_active == True)
    )
    helpers = helpers_result.scalars().all()

    performance = []
    for h in helpers:
        a_result = await db.execute(
            select(TaskAssignment).where(TaskAssignment.helper_id == h.id)
        )
        assignments = a_result.scalars().all()
        total = len(assignments)
        completed = sum(1 for a in assignments if a.status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED))
        overdue = sum(1 for a in assignments if a.status == TaskStatus.OVERDUE)
        performance.append({
            "helper_id": h.id,
            "full_name": h.full_name,
            "phone": h.phone,
            "total_tasks": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
        })

    performance.sort(key=lambda x: x["completion_rate"], reverse=True)
    return performance


@router.get("/event-wise/{event_id}")
async def event_wise_report(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event:
        return {"error": "Event not found"}

    tasks_result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignments))
        .where(Task.event_id == event_id, Task.is_active == True)
    )
    tasks = tasks_result.scalars().all()

    all_assignments = []
    for t in tasks:
        all_assignments.extend(t.assignments)

    return {
        "event": {"id": event.id, "name": event.name},
        "total_assigned": len(all_assignments),
        "completed": sum(1 for a in all_assignments if a.status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)),
        "in_progress": sum(1 for a in all_assignments if a.status == TaskStatus.IN_PROGRESS),
        "pending": sum(1 for a in all_assignments if a.status in (TaskStatus.ASSIGNED, TaskStatus.NEW, TaskStatus.ACKNOWLEDGED)),
        "overdue": sum(1 for a in all_assignments if a.status == TaskStatus.OVERDUE),
        "assignments": [
            {
                "assignment_id": a.id,
                "helper_id": a.helper_id,
                "task_id": a.task_id,
                "status": a.status.value,
                "assigned_at": a.assigned_at.isoformat(),
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in all_assignments
        ],
    }


@router.get("/overdue")
async def overdue_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    today = date.today()
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignments))
        .where(
            Task.is_active == True,
            Task.due_date < today,
            Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CANCELLED]),
        )
        .order_by(Task.due_date)
    )
    tasks = result.scalars().all()
    return [
        {
            "task_id": t.id,
            "title": t.title,
            "priority": t.priority.value,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status.value,
            "days_overdue": (today - t.due_date).days if t.due_date else None,
            "helpers": [{"helper_id": a.helper_id, "status": a.status.value} for a in t.assignments],
        }
        for t in tasks
    ]
