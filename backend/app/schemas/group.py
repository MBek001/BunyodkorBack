from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    schedule: Optional[str] = None  # JSON string
    max_students: Optional[int] = 20


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    schedule: Optional[str] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None


class GroupResponse(GroupBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
