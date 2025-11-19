from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    PAYME = "payme"
    CLICK = "click"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True, index=True)
    payment_date = Column(DateTime, default=datetime.utcnow)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="payments")
    contract = relationship("Contract", back_populates="payments")


class ErrorPayment(Base):
    __tablename__ = "error_payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    transaction_id = Column(String, nullable=True)
    error_reason = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
