from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User
from app.models.audit import AuditLog
from app.models.enums import UserRole

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    old_value: str | None
    new_value: str | None
    created_at: datetime


@router.get("/", response_model=list[AuditLogOut])
async def list_audit_logs(
    action: str | None = None,
    entity_type: str | None = None,
    user_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    q = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        q = q.where(AuditLog.action == action)
    if entity_type:
        q = q.where(AuditLog.entity_type == entity_type)
    if user_id:
        q = q.where(AuditLog.user_id == user_id)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
