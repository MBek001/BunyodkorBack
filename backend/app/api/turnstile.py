from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.turnstile import TurnstileLog
from app.models.student import Student
from app.models.contract import Contract, ContractStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.turnstile import (
    TurnstileLogCreate, TurnstileLogResponse,
    TurnstileVerificationRequest, TurnstileVerificationResponse
)
from app.api.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.post("/verify", response_model=TurnstileVerificationResponse)
async def verify_student_access(
    verification_request: TurnstileVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify if student can access the building.
    Called by turnstile device with FaceID recognition result.
    """
    student = db.query(Student).filter(Student.id == verification_request.student_id).first()

    if not student:
        return TurnstileVerificationResponse(
            access_granted=False,
            student_name="Unknown",
            payment_verified=False,
            message="Student not found in database"
        )

    if not student.is_active:
        log = TurnstileLog(
            student_id=student.id,
            turnstile_id=verification_request.turnstile_id,
            access_granted=False,
            payment_verified=False,
            face_match_confidence=verification_request.face_match_confidence,
            notes="Student account is inactive"
        )
        db.add(log)
        db.commit()

        return TurnstileVerificationResponse(
            access_granted=False,
            student_name=f"{student.first_name} {student.last_name}",
            payment_verified=False,
            message="Student account is inactive"
        )

    # Get active contract
    active_contract = db.query(Contract).filter(
        Contract.student_id == student.id,
        Contract.status == ContractStatus.ACTIVE
    ).first()

    if not active_contract:
        log = TurnstileLog(
            student_id=student.id,
            turnstile_id=verification_request.turnstile_id,
            access_granted=False,
            payment_verified=False,
            face_match_confidence=verification_request.face_match_confidence,
            notes="No active contract"
        )
        db.add(log)
        db.commit()

        return TurnstileVerificationResponse(
            access_granted=False,
            student_name=f"{student.first_name} {student.last_name}",
            payment_verified=False,
            message="No active contract found"
        )

    # Check if payment for current month exists
    current_month = datetime.now().month
    current_year = datetime.now().year

    payment = db.query(Payment).filter(
        Payment.contract_id == active_contract.id,
        Payment.month == current_month,
        Payment.year == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).first()

    payment_verified = payment is not None
    access_granted = payment_verified

    log = TurnstileLog(
        student_id=student.id,
        turnstile_id=verification_request.turnstile_id,
        access_granted=access_granted,
        payment_verified=payment_verified,
        face_match_confidence=verification_request.face_match_confidence,
        notes=f"Payment {'verified' if payment_verified else 'not found'} for {current_month}/{current_year}"
    )
    db.add(log)
    db.commit()

    message = "Access granted" if access_granted else f"Payment not found for {current_month}/{current_year}"

    return TurnstileVerificationResponse(
        access_granted=access_granted,
        student_name=f"{student.first_name} {student.last_name}",
        payment_verified=payment_verified,
        message=message
    )


@router.post("/", response_model=TurnstileLogResponse)
async def create_turnstile_log(
    log_data: TurnstileLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Manually create a turnstile log (for testing or admin purposes)"""
    log = TurnstileLog(**log_data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=List[TurnstileLogResponse])
async def get_turnstile_logs(
    skip: int = 0,
    limit: int = 100,
    student_id: int = None,
    access_granted: bool = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get turnstile logs with optional filters"""
    query = db.query(TurnstileLog)

    if student_id:
        query = query.filter(TurnstileLog.student_id == student_id)
    if access_granted is not None:
        query = query.filter(TurnstileLog.access_granted == access_granted)
    if start_date:
        query = query.filter(TurnstileLog.entry_time >= start_date)
    if end_date:
        query = query.filter(TurnstileLog.entry_time <= end_date)

    logs = query.order_by(TurnstileLog.entry_time.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/{log_id}", response_model=TurnstileLogResponse)
async def get_turnstile_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get turnstile log by ID"""
    log = db.query(TurnstileLog).filter(TurnstileLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Turnstile log not found")
    return log


@router.get("/student/{student_id}/today")
async def get_student_today_access(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if student accessed building today"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    logs = db.query(TurnstileLog).filter(
        TurnstileLog.student_id == student_id,
        TurnstileLog.entry_time >= today_start,
        TurnstileLog.entry_time < today_end,
        TurnstileLog.access_granted == True
    ).all()

    return {
        "student_id": student_id,
        "accessed_today": len(logs) > 0,
        "access_count": len(logs),
        "logs": logs
    }
