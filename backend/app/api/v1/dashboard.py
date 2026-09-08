from datetime import date, datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.models.task import Task, TaskAssignment, TaskFollowup
from app.models.enums import UserRole, TaskStatus, TaskPriority

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Role-aware dashboard statistics."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    if current_user.role == UserRole.HELPER:
        # Only own assignments
        base = select(TaskAssignment).where(TaskAssignment.helper_id == current_user.id)
        result = await db.execute(base)
        assignments = result.scalars().all()

        stats = {
            "my_tasks": len(assignments),
            "pending": sum(1 for a in assignments if a.status in (TaskStatus.ASSIGNED, TaskStatus.NEW)),
            "in_progress": sum(1 for a in assignments if a.status == TaskStatus.IN_PROGRESS),
            "waiting": sum(1 for a in assignments if a.status == TaskStatus.WAITING),
            "completed": sum(1 for a in assignments if a.status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)),
            "overdue": sum(1 for a in assignments if a.status == TaskStatus.OVERDUE),
        }
        return {"role": "helper", "stats": stats}

    # Shura / Assistant / Admin – overall task view
    result = await db.execute(select(Task).where(Task.is_active == True))
    tasks = result.scalars().all()

    assign_result = await db.execute(select(TaskAssignment))
    assignments = assign_result.scalars().all()

    # Overdue: due_date < today and not completed/verified
    overdue_count = 0
    for t in tasks:
        if t.due_date and t.due_date < today and t.status not in (TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CANCELLED):
            overdue_count += 1

    critical = sum(1 for t in tasks if t.priority == TaskPriority.CRITICAL)
    followups_needed = sum(1 for t in tasks if t.status == TaskStatus.FOLLOWUP_REQUIRED)

    stats = {
        "total_tasks": len(tasks),
        "completed": sum(1 for t in tasks if t.status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)),
        "pending": sum(1 for t in tasks if t.status in (TaskStatus.NEW, TaskStatus.ASSIGNED)),
        "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
        "overdue": overdue_count,
        "critical": critical,
        "followups_required": followups_needed,
    }

    # Today's / tomorrow due
    due_today = sum(1 for t in tasks if t.due_date == today)
    due_tomorrow = sum(1 for t in tasks if t.due_date == tomorrow)

    extra = {
        "due_today": due_today,
        "due_tomorrow": due_tomorrow,
        "total_assignments": len(assignments),
    }

    # Assistant-focused extras
    if current_user.role in (UserRole.ASSISTANT, UserRole.ADMIN, UserRole.SHURA_MEMBER):
        fu_result = await db.execute(
            select(func.count()).select_from(TaskFollowup).where(
                TaskFollowup.created_at >= datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            )
        )
        extra["followups_today"] = fu_result.scalar() or 0

    return {"role": current_user.role.value, "stats": stats, "extra": extra}


@router.get("/recent-tasks")
async def recent_tasks(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.HELPER:
        q = (
            select(TaskAssignment, Task)
            .join(Task, Task.id == TaskAssignment.task_id)
            .where(TaskAssignment.helper_id == current_user.id)
            .order_by(TaskAssignment.updated_at.desc())
            .limit(limit)
        )
        result = await db.execute(q)
        rows = result.all()
        return [
            {
                "assignment_id": a.id,
                "task_id": t.id,
                "title": t.title,
                "status": a.status.value,
                "priority": t.priority.value,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "updated_at": a.updated_at.isoformat(),
            }
            for a, t in rows
        ]

    q = select(Task).where(Task.is_active == True).order_by(Task.updated_at.desc()).limit(limit)
    result = await db.execute(q)
    tasks = result.scalars().all()
    return [
        {
            "task_id": t.id,
            "title": t.title,
            "status": t.status.value,
            "priority": t.priority.value,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "updated_at": t.updated_at.isoformat(),
        }
        for t in tasks
    ]
