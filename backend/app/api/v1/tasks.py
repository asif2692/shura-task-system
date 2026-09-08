from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.models.task import Task, TaskAssignment, TaskStatusHistory, TaskFollowup
from app.models.enums import UserRole, TaskStatus, TaskPriority
from app.models.audit import AuditLog
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskOut, TaskAssignmentOut,
    AssignmentStatusUpdate, AssignmentVerify, FollowupCreate, FollowupOut,
)
from app.services.notifications import notify_helpers_new_task, notify_status_update

router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def _log_audit(db: AsyncSession, user_id: int, action: str, entity_type: str, entity_id: int,
                     old_value: str | None = None, new_value: str | None = None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(log)


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    # Validate helpers exist and are HELPER role
    helpers_result = await db.execute(
        select(User).where(User.id.in_(payload.helper_ids), User.role == UserRole.HELPER, User.is_active == True)
    )
    helpers = helpers_result.scalars().all()
    if len(helpers) != len(set(payload.helper_ids)):
        raise HTTPException(status_code=400, detail="One or more helper IDs are invalid or inactive")

    task = Task(
        title=payload.title,
        description=payload.description,
        created_by=current_user.id,
        event_id=payload.event_id,
        category=payload.category,
        priority=payload.priority,
        priority_set_by=current_user.id,
        priority_set_at=datetime.now(timezone.utc),
        start_date=payload.start_date,
        due_date=payload.due_date,
        due_time=payload.due_time,
        notes=payload.notes,
        status=TaskStatus.ASSIGNED,
    )
    db.add(task)
    await db.flush()

    for helper in helpers:
        assignment = TaskAssignment(
            task_id=task.id,
            helper_id=helper.id,
            status=TaskStatus.ASSIGNED,
        )
        db.add(assignment)

        # Status history
        hist = TaskStatusHistory(
            task_id=task.id,
            assignment_id=None,  # will update after flush if needed
            old_status=None,
            new_status=TaskStatus.ASSIGNED,
            changed_by=current_user.id,
            note=f"Assigned to {helper.full_name}",
        )
        db.add(hist)

    await _log_audit(db, current_user.id, "task_created", "task", task.id, new_value=task.title)
    await notify_helpers_new_task(db, [h.id for h in helpers], task.id, task.title)
    await db.commit()

    # Reload with assignments
    result = await db.execute(
        select(Task).options(selectinload(Task.assignments)).where(Task.id == task.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    event_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Task).options(selectinload(Task.assignments)).where(Task.is_active == True)

    # Helpers only see their own assigned tasks
    if current_user.role == UserRole.HELPER:
        q = q.join(TaskAssignment).where(TaskAssignment.helper_id == current_user.id)

    if status:
        q = q.where(Task.status == status)
    if priority:
        q = q.where(Task.priority == priority)
    if event_id:
        q = q.where(Task.event_id == event_id)

    q = q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().unique().all()


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.assignments)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role == UserRole.HELPER:
        helper_ids = [a.helper_id for a in task.assignments]
        if current_user.id not in helper_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.assignments)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    if "priority" in data and data["priority"] != task.priority:
        task.previous_priority = task.priority
        task.priority_set_by = current_user.id
        task.priority_set_at = datetime.now(timezone.utc)
        await _log_audit(
            db, current_user.id, "priority_changed", "task", task.id,
            old_value=str(task.priority), new_value=str(data["priority"])
        )

    for k, v in data.items():
        setattr(task, k, v)

    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/assignments/{assignment_id}/status", response_model=TaskAssignmentOut)
async def update_assignment_status(
    assignment_id: int,
    payload: AssignmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(TaskAssignment).where(TaskAssignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Helper can only update own assignment
    if current_user.role == UserRole.HELPER and assignment.helper_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    old_status = assignment.status
    assignment.status = payload.status

    if payload.status == TaskStatus.ACKNOWLEDGED:
        assignment.acknowledged_at = datetime.now(timezone.utc)
    elif payload.status == TaskStatus.COMPLETED:
        assignment.completed_at = datetime.now(timezone.utc)
        if payload.completion_note:
            assignment.completion_note = payload.completion_note

    if payload.delay_reason_code:
        assignment.delay_reason_code = payload.delay_reason_code
        assignment.delay_reason_detail = payload.delay_reason_detail

    hist = TaskStatusHistory(
        task_id=assignment.task_id,
        assignment_id=assignment.id,
        old_status=old_status,
        new_status=payload.status,
        changed_by=current_user.id,
        note=payload.note or payload.completion_note,
    )
    db.add(hist)
    await _log_audit(
        db, current_user.id, "status_changed", "assignment", assignment.id,
        old_value=str(old_status), new_value=str(payload.status)
    )
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.post("/assignments/{assignment_id}/verify", response_model=TaskAssignmentOut)
async def verify_assignment(
    assignment_id: int,
    payload: AssignmentVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    result = await db.execute(select(TaskAssignment).where(TaskAssignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Only completed tasks can be verified")

    assignment.status = TaskStatus.VERIFIED
    assignment.verified_at = datetime.now(timezone.utc)
    assignment.verified_by = current_user.id

    hist = TaskStatusHistory(
        task_id=assignment.task_id,
        assignment_id=assignment.id,
        old_status=TaskStatus.COMPLETED,
        new_status=TaskStatus.VERIFIED,
        changed_by=current_user.id,
        note=payload.note,
    )
    db.add(hist)
    await _log_audit(db, current_user.id, "task_verified", "assignment", assignment.id)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.post("/{task_id}/followups", response_model=FollowupOut, status_code=status.HTTP_201_CREATED)
async def create_followup(
    task_id: int,
    payload: FollowupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    followup = TaskFollowup(
        task_id=task_id,
        assignment_id=payload.assignment_id,
        followup_by=current_user.id,
        followup_to=payload.followup_to,
        response=payload.response,
        delay_reason_code=payload.delay_reason_code,
        delay_reason_detail=payload.delay_reason_detail,
        next_followup_date=payload.next_followup_date,
        notes=payload.notes,
    )
    db.add(followup)
    await _log_audit(db, current_user.id, "followup_created", "task", task_id)
    await db.commit()
    await db.refresh(followup)
    return followup


@router.get("/{task_id}/followups", response_model=list[FollowupOut])
async def list_followups(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TaskFollowup).where(TaskFollowup.task_id == task_id).order_by(TaskFollowup.created_at)
    )
    return result.scalars().all()
