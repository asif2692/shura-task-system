from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    tasks,
    events,
    groups,
    notifications,
    dashboard,
    reports,
    audit,
    whatsapp,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(events.router)
api_router.include_router(groups.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
api_router.include_router(whatsapp.router)
