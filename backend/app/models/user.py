from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)  # for WhatsApp
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, native_enum=False), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Optional links
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    group = relationship("Group", back_populates="members", foreign_keys=[group_id])
    created_tasks = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by")
    assignments = relationship("TaskAssignment", back_populates="helper", foreign_keys="TaskAssignment.helper_id")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
