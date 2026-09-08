from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    responsible_person_id: int | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    responsible_person_id: int | None = None


class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
