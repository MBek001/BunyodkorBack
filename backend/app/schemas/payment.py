from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    student_id: int
    contract_id: int
    amount: float
    payment_method: PaymentMethod
    month: int
    year: int
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(PaymentCreate):
    id: int
    payment_status: PaymentStatus
    payment_date: datetime
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorPaymentResponse(BaseModel):
    id: int
    contract_number: str
    amount: float
    payment_method: PaymentMethod
    transaction_id: Optional[str]
    error_reason: str
    is_resolved: bool
    resolved_student_id: Optional[int]
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ParentPaymentRequest(BaseModel):
    contract_number: str


class ParentPaymentInfo(BaseModel):
    student_name: str
    group_name: Optional[str]
    monthly_fee: float
    discount_percentage: float
    final_fee: float
    contract_id: int
