from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.models.event import Event
from app.models.enums import UserRole
from app.models.audit import AuditLog
from app.schemas.event import EventCreate, EventUpdate, EventOut

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    event = Event(**payload.model_dump())
    db.add(event)
    db.add(AuditLog(user_id=current_user.id, action="event_created", entity_type="event", entity_id=None, new_value=payload.name))
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/", response_model=list[EventOut])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Event).order_by(Event.start_date.desc().nullslast()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: int,
    payload: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SHURA_MEMBER, UserRole.ASSISTANT)),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(event, k, v)
    db.add(AuditLog(user_id=current_user.id, action="event_updated", entity_type="event", entity_id=event_id))
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    db.add(AuditLog(user_id=current_user.id, action="event_deleted", entity_type="event", entity_id=event_id))
    await db.commit()
