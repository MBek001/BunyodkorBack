from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.payment import Payment, ErrorPayment, PaymentMethod, PaymentStatus
from app.models.contract import Contract
from app.models.student import Student
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, ErrorPaymentResponse,
    ParentPaymentRequest, ParentPaymentInfo
)
from app.api.dependencies import get_current_user, get_current_admin, get_current_superuser_or_admin

router = APIRouter()


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Create a payment (for cash payments by admin)"""
    # Verify student exists
    student = db.query(Student).filter(Student.id == payment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == payment_data.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    payment = Payment(
        **payment_data.dict(),
        payment_status=PaymentStatus.COMPLETED,
        created_by=current_user.id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    student_id: int = None,
    contract_id: int = None,
    payment_status: PaymentStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments with optional filters"""
    query = db.query(Payment)

    if student_id:
        query = query.filter(Payment.student_id == student_id)
    if contract_id:
        query = query.filter(Payment.contract_id == contract_id)
    if payment_status:
        query = query.filter(Payment.payment_status == payment_status)

    payments = query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment by ID"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


# Parent Payment Portal Endpoints
@router.post("/parent/info", response_model=ParentPaymentInfo)
async def get_payment_info_for_parent(
    request: ParentPaymentRequest,
    db: Session = Depends(get_db)
):
    """Get payment information for parents by contract number"""
    contract = db.query(Contract).filter(
        Contract.contract_number == request.contract_number
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found. Please check the contract number."
        )

    student = db.query(Student).filter(Student.id == contract.student_id).first()

    group_name = None
    if student.group:
        group_name = student.group.name

    return ParentPaymentInfo(
        student_name=f"{student.first_name} {student.last_name}",
        group_name=group_name,
        monthly_fee=contract.monthly_fee,
        discount_percentage=contract.discount_percentage,
        final_fee=contract.final_monthly_fee,
        contract_id=contract.id
    )


@router.post("/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for Payme payment notifications"""
    # TODO: Implement Payme integration
    # This is a placeholder for Payme payment processing
    data = await request.json()

    # Verify payment signature
    # Process payment based on Payme's API
    # Create payment record or error payment record

    return {"message": "Payme webhook received"}


@router.post("/click/webhook")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for Click payment notifications"""
    # TODO: Implement Click integration
    # This is a placeholder for Click payment processing
    data = await request.json()

    # Verify payment signature
    # Process payment based on Click's API
    # Create payment record or error payment record

    return {"message": "Click webhook received"}


# Error Payments Management
@router.get("/errors/", response_model=List[ErrorPaymentResponse])
async def get_error_payments(
    skip: int = 0,
    limit: int = 100,
    is_resolved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all error payments"""
    query = db.query(ErrorPayment).filter(ErrorPayment.is_resolved == is_resolved)
    error_payments = query.offset(skip).limit(limit).all()
    return error_payments


@router.post("/errors/{error_payment_id}/resolve")
async def resolve_error_payment(
    error_payment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Resolve an error payment by assigning it to correct student"""
    error_payment = db.query(ErrorPayment).filter(
        ErrorPayment.id == error_payment_id
    ).first()

    if not error_payment:
        raise HTTPException(status_code=404, detail="Error payment not found")

    if error_payment.is_resolved:
        raise HTTPException(
            status_code=400,
            detail="This error payment has already been resolved"
        )

    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get active contract for student
    contract = db.query(Contract).filter(
        Contract.student_id == student_id,
        Contract.status == "active"
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="No active contract found for this student"
        )

    # Create actual payment
    payment = Payment(
        student_id=student_id,
        contract_id=contract.id,
        amount=error_payment.amount,
        payment_method=error_payment.payment_method,
        payment_status=PaymentStatus.COMPLETED,
        transaction_id=error_payment.transaction_id,
        payment_date=datetime.utcnow(),
        month=datetime.utcnow().month,
        year=datetime.utcnow().year,
        notes=f"Resolved from error payment #{error_payment_id}",
        created_by=current_user.id
    )
    db.add(payment)

    # Mark error payment as resolved
    error_payment.is_resolved = True
    error_payment.resolved_student_id = student_id
    error_payment.resolved_by = current_user.id
    error_payment.resolved_at = datetime.utcnow()

    db.commit()

    return {"message": "Error payment resolved successfully"}


@router.delete("/errors/{error_payment_id}")
async def delete_error_payment(
    error_payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete an error payment"""
    error_payment = db.query(ErrorPayment).filter(
        ErrorPayment.id == error_payment_id
    ).first()

    if not error_payment:
        raise HTTPException(status_code=404, detail="Error payment not found")

    db.delete(error_payment)
    db.commit()

    return {"message": "Error payment deleted successfully"}
