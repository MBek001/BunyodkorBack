from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TurnstileLogCreate(BaseModel):
    student_id: int
    turnstile_id: Optional[str] = None
    access_granted: bool
    payment_verified: bool
    face_match_confidence: Optional[int] = None
    notes: Optional[str] = None


class TurnstileLogResponse(TurnstileLogCreate):
    id: int
    entry_time: datetime
    exit_time: Optional[datetime]

    class Config:
        from_attributes = True


class TurnstileVerificationRequest(BaseModel):
    """Request from turnstile device to verify student access"""
    student_id: int
    face_match_confidence: int
    turnstile_id: str


class TurnstileVerificationResponse(BaseModel):
    """Response to turnstile device"""
    access_granted: bool
    student_name: str
    payment_verified: bool
    message: str
