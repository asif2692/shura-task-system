from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GroupBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None


class GroupOut(GroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
