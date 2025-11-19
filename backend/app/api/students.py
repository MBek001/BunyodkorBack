from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import pandas as pd
from io import BytesIO
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.contract import Contract, ContractStatus
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.api.dependencies import get_current_admin, get_current_superuser_or_admin, get_current_user, check_permission

router = APIRouter()


@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Create a new student"""
    student = Student(**student_data.dict())
    db.add(student)
    db.flush()  # Get the student ID

    # Create user account for student login
    # Username: enrollment_year + student_id
    username = f"{student.enrollment_year}{student.id}"
    password = username  # Default password same as username

    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        full_name=f"{student.first_name} {student.last_name}",
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.flush()

    student.user_id = user.id
    db.commit()
    db.refresh(student)

    return student


@router.get("/", response_model=List[StudentResponse])
async def get_students(
    skip: int = 0,
    limit: int = 100,
    group_id: int = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all students with optional filters"""
    query = db.query(Student)

    if group_id:
        query = query.filter(Student.group_id == group_id)
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)

    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Update student information"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for field, value in student_data.dict(exclude_unset=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.post("/import-excel")
async def import_students_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Import students from Excel file.
    Expected columns: first_name, last_name, date_of_birth, parent_phone,
                      enrollment_year, group_name, monthly_fee, discount_percentage
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        required_columns = ['first_name', 'last_name', 'date_of_birth', 'parent_phone',
                           'enrollment_year', 'monthly_fee']

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Get or create group if group_name provided
                group_id = None
                if 'group_name' in df.columns and pd.notna(row['group_name']):
                    group = db.query(Group).filter(Group.name == row['group_name']).first()
                    if group:
                        group_id = group.id

                # Create student
                student = Student(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    middle_name=row.get('middle_name'),
                    date_of_birth=pd.to_datetime(row['date_of_birth']).date(),
                    parent_phone=str(row['parent_phone']),
                    parent_name=row.get('parent_name'),
                    enrollment_year=int(row['enrollment_year']),
                    group_id=group_id,
                    is_active=True
                )
                db.add(student)
                db.flush()

                # Create user account
                username = f"{student.enrollment_year}{student.id}"
                password = username

                user = User(
                    username=username,
                    hashed_password=get_password_hash(password),
                    full_name=f"{student.first_name} {student.last_name}",
                    role=UserRole.STUDENT,
                    is_active=True
                )
                db.add(user)
                db.flush()

                student.user_id = user.id

                # Create contract
                monthly_fee = float(row['monthly_fee'])
                discount_percentage = float(row.get('discount_percentage', 0))
                discount_amount = monthly_fee * (discount_percentage / 100)
                final_fee = monthly_fee - discount_amount

                contract_number = f"{datetime.now().year}{student.id:06d}"
                contract = Contract(
                    contract_number=contract_number,
                    student_id=student.id,
                    monthly_fee=monthly_fee,
                    discount_percentage=discount_percentage,
                    discount_amount=discount_amount,
                    final_monthly_fee=final_fee,
                    status=ContractStatus.ACTIVE,
                    start_date=datetime.utcnow()
                )
                db.add(contract)

                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")

        db.commit()

        return {
            "message": f"Successfully imported {imported_count} students",
            "imported": imported_count,
            "errors": errors if errors else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
