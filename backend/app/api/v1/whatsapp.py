"""
WhatsApp Quick Message – NO paid API.
Generates a wa.me link with pre-filled message.
Frontend opens this URL; user presses Send manually.
"""
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.models.task import Task, TaskAssignment
from app.models.enums import UserRole

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Quick Message"])


class WhatsAppLinkOut(BaseModel):
    helper_id: int
    helper_name: str
    phone: str | None
    message: str
    wa_url: str | None  # null if no phone


def _build_message(helper_name: str, task: Task) -> str:
    due = ""
    if task.due_date:
        due = f"Deadline: {task.due_date.strftime('%d %B %Y')}"
        if task.due_time:
            due += f" Time: {task.due_time.strftime('%I:%M %p')}"
    msg = (
        f"السلام علیکم {helper_name}،\n\n"
        f"آپ کو ایک نیا کام تفویض کیا گیا ہے۔\n\n"
        f"کام: {task.title}\n"
        f"Priority: {task.priority.value.upper()}\n"
    )
    if due:
        msg += f"{due}\n"
    msg += "\nبراہ کرم مقررہ وقت تک کام مکمل کریں۔\n\nشکریہ"
    return msg


def _phone_to_wa(phone: str | None) -> str | None:
    if not phone:
        return None
    # Keep digits only, assume Pakistan if starts with 0
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = "92" + digits[1:]
    if not digits.startswith("92") and len(digits) == 10:
        digits = "92" + digits
    return digits


@router.get("/task/{task_id}/helper/{helper_id}", response_model=WhatsAppLinkOut)
async def whatsapp_for_helper(
    task_id: int,
    helper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    helper_result = await db.execute(select(User).where(User.id == helper_id, User.role == UserRole.HELPER))
    helper = helper_result.scalar_one_or_none()
    if not helper:
        raise HTTPException(status_code=404, detail="Helper not found")

    # Ensure this helper is assigned
    assign_result = await db.execute(
        select(TaskAssignment).where(
            TaskAssignment.task_id == task_id,
            TaskAssignment.helper_id == helper_id,
        )
    )
    if not assign_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Helper is not assigned to this task")

    message = _build_message(helper.full_name, task)
    phone = _phone_to_wa(helper.phone)
    wa_url = None
    if phone:
        wa_url = f"https://wa.me/{phone}?text={quote(message)}"

    return WhatsAppLinkOut(
        helper_id=helper.id,
        helper_name=helper.full_name,
        phone=helper.phone,
        message=message,
        wa_url=wa_url,
    )


@router.get("/task/{task_id}", response_model=list[WhatsAppLinkOut])
async def whatsapp_for_all_helpers(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    """Group task: one WhatsApp link per assigned helper."""
    result = await db.execute(
        select(Task).options(selectinload(Task.assignments)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    links = []
    for a in task.assignments:
        helper_result = await db.execute(select(User).where(User.id == a.helper_id))
        helper = helper_result.scalar_one_or_none()
        if not helper:
            continue
        message = _build_message(helper.full_name, task)
        phone = _phone_to_wa(helper.phone)
        wa_url = f"https://wa.me/{phone}?text={quote(message)}" if phone else None
        links.append(
            WhatsAppLinkOut(
                helper_id=helper.id,
                helper_name=helper.full_name,
                phone=helper.phone,
                message=message,
                wa_url=wa_url,
            )
        )
    return links
