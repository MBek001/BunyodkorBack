from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.models.student import Student
from app.schemas.contract import ContractCreate, ContractUpdate, ContractResponse
from app.api.dependencies import get_current_admin, get_current_superuser_or_admin, get_current_user

router = APIRouter()


@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Create a new contract"""
    student = db.query(Student).filter(Student.id == contract_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Calculate final monthly fee
    discount_amount = contract_data.monthly_fee * (contract_data.discount_percentage / 100)
    final_fee = contract_data.monthly_fee - discount_amount - contract_data.discount_amount

    # Generate contract number: YEAR + STUDENT_ID (padded)
    contract_number = f"{datetime.now().year}{student.id:06d}"

    # Check if contract already exists
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if existing_contract:
        # If exists, generate with timestamp
        contract_number = f"{datetime.now().year}{student.id:06d}{int(datetime.now().timestamp())}"

    contract = Contract(
        contract_number=contract_number,
        student_id=contract_data.student_id,
        monthly_fee=contract_data.monthly_fee,
        discount_percentage=contract_data.discount_percentage,
        discount_amount=contract_data.discount_amount,
        final_monthly_fee=final_fee,
        status=ContractStatus.ACTIVE,
        start_date=contract_data.start_date,
        notes=contract_data.notes
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/", response_model=List[ContractResponse])
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    student_id: int = None,
    status: ContractStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contracts with optional filters"""
    query = db.query(Contract)

    if student_id:
        query = query.filter(Contract.student_id == student_id)
    if status:
        query = query.filter(Contract.status == status)

    contracts = query.offset(skip).limit(limit).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contract by ID"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/number/{contract_number}", response_model=ContractResponse)
async def get_contract_by_number(
    contract_number: str,
    db: Session = Depends(get_db)
):
    """Get contract by contract number (for parent payment portal)"""
    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    return contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Update contract information"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = contract_data.dict(exclude_unset=True)

    # Recalculate final fee if monthly_fee or discounts changed
    if any(key in update_data for key in ['monthly_fee', 'discount_percentage', 'discount_amount']):
        monthly_fee = update_data.get('monthly_fee', contract.monthly_fee)
        discount_percentage = update_data.get('discount_percentage', contract.discount_percentage)
        discount_amount = update_data.get('discount_amount', contract.discount_amount)

        calculated_discount = monthly_fee * (discount_percentage / 100)
        final_fee = monthly_fee - calculated_discount - discount_amount
        update_data['final_monthly_fee'] = final_fee

    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)
    return contract


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    db.delete(contract)
    db.commit()
    return {"message": "Contract deleted successfully"}
