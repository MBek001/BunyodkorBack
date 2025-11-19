from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.contract import ContractStatus


class ContractBase(BaseModel):
    student_id: int
    monthly_fee: float
    discount_percentage: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    notes: Optional[str] = None


class ContractCreate(ContractBase):
    start_date: datetime


class ContractUpdate(BaseModel):
    monthly_fee: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[ContractStatus] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ContractResponse(ContractBase):
    id: int
    contract_number: str
    final_monthly_fee: float
    status: ContractStatus
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
