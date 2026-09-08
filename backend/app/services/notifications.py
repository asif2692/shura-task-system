"""
In-app notification helpers.
Email sending can be added later using SMTP settings.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    *,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_task_id: int | None = None,
    related_assignment_id: int | None = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_task_id=related_task_id,
        related_assignment_id=related_assignment_id,
    )
    db.add(notif)
    return notif


async def notify_helpers_new_task(
    db: AsyncSession,
    helper_ids: list[int],
    task_id: int,
    task_title: str,
):
    for hid in helper_ids:
        await create_notification(
            db,
            user_id=hid,
            title="نیا ٹاسک",
            message=f"آپ کو ایک نئی Task assign ہوئی ہے: {task_title}",
            notification_type="new_task",
            related_task_id=task_id,
        )


async def notify_status_update(
    db: AsyncSession,
    user_ids: list[int],
    task_id: int,
    helper_name: str,
    new_status: str,
):
    for uid in user_ids:
        await create_notification(
            db,
            user_id=uid,
            title="Status Update",
            message=f"{helper_name} نے Task کو {new_status} کر دیا ہے۔",
            notification_type="status_update",
            related_task_id=task_id,
        )
