from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: date
    phone_number: Optional[str] = None
    parent_phone: str
    parent_name: Optional[str] = None
    address: Optional[str] = None
    enrollment_year: int
    group_id: Optional[int] = None
    notes: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    address: Optional[str] = None
    group_id: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int]
    photo_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentImport(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: str  # Will be converted to date
    parent_phone: str
    parent_name: Optional[str] = None
    enrollment_year: int
    group_name: Optional[str] = None
    monthly_fee: float
    discount_percentage: Optional[float] = 0.0
