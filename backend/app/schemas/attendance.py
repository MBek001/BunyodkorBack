from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from app.models.attendance import AttendanceStatus


class SessionCreate(BaseModel):
    group_id: int
    session_date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None


class SessionResponse(SessionCreate):
    id: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    session_id: int
    student_id: int
    status: AttendanceStatus
    entered_building: Optional[bool] = False
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    entered_building: Optional[bool] = None
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: AttendanceStatus
    entered_building: bool
    notes: Optional[str]
    marked_by: Optional[int]
    marked_at: datetime

    class Config:
        from_attributes = True
