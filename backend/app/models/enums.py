import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SHURA_MEMBER = "shura_member"
    ASSISTANT = "assistant"
    HELPER = "helper"


class TaskPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    FOLLOWUP_REQUIRED = "followup_required"
    OVERDUE = "overdue"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class DelayReasonCode(str, enum.Enum):
    PERSON_NOT_AVAILABLE = "person_not_available"
    INFO_NOT_RECEIVED = "info_not_received"
    RESOURCES_NOT_AVAILABLE = "resources_not_available"
    PERMISSION_REQUIRED = "permission_required"
    INSUFFICIENT_TIME = "insufficient_time"
    MISUNDERSTANDING = "misunderstanding"
    ILLNESS_LEAVE = "illness_leave"
    OTHER = "other"
