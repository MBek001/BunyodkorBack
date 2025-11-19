from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.payment import Payment, PaymentStatus
from app.models.contract import Contract, ContractStatus
from app.models.attendance import Attendance, Session as TrainingSession, AttendanceStatus
from app.models.group import Group
from app.api.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get dashboard statistics for admin"""
    # Total students
    total_students = db.query(func.count(Student.id)).scalar()
    active_students = db.query(func.count(Student.id)).filter(Student.is_active == True).scalar()
    inactive_students = total_students - active_students

    # Today's revenue
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.payment_date >= today_start,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0

    # This month's revenue
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = db.query(func.sum(Payment.amount)).filter(
        extract('month', Payment.payment_date) == current_month,
        extract('year', Payment.payment_date) == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0

    # This year's revenue
    yearly_revenue = db.query(func.sum(Payment.amount)).filter(
        extract('year', Payment.payment_date) == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0

    # Students with no payment this month
    students_with_payment = db.query(Payment.student_id).filter(
        Payment.month == current_month,
        Payment.year == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).distinct().subquery()

    debtors_count = db.query(func.count(Student.id)).filter(
        Student.is_active == True,
        ~Student.id.in_(students_with_payment)
    ).scalar()

    # Total groups
    total_groups = db.query(func.count(Group.id)).scalar()
    active_groups = db.query(func.count(Group.id)).filter(Group.is_active == True).scalar()

    return {
        "students": {
            "total": total_students,
            "active": active_students,
            "inactive": inactive_students
        },
        "revenue": {
            "today": float(today_revenue),
            "monthly": float(monthly_revenue),
            "yearly": float(yearly_revenue)
        },
        "debtors": debtors_count,
        "groups": {
            "total": total_groups,
            "active": active_groups
        }
    }


@router.get("/revenue/monthly")
async def get_monthly_revenue_report(
    year: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get monthly revenue breakdown for a year"""
    if not year:
        year = datetime.now().year

    monthly_data = []
    for month in range(1, 13):
        revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.month == month,
            Payment.year == year,
            Payment.payment_status == PaymentStatus.COMPLETED
        ).scalar() or 0

        payment_count = db.query(func.count(Payment.id)).filter(
            Payment.month == month,
            Payment.year == year,
            Payment.payment_status == PaymentStatus.COMPLETED
        ).scalar()

        monthly_data.append({
            "month": month,
            "revenue": float(revenue),
            "payment_count": payment_count
        })

    return {
        "year": year,
        "monthly_data": monthly_data,
        "total_revenue": sum(m["revenue"] for m in monthly_data)
    }


@router.get("/debtors")
async def get_debtors_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get list of students who haven't paid for current month"""
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get students who paid this month
    students_with_payment = db.query(Payment.student_id).filter(
        Payment.month == current_month,
        Payment.year == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).distinct().subquery()

    # Get active students who haven't paid
    debtors = db.query(Student).join(Contract).filter(
        Student.is_active == True,
        Contract.status == ContractStatus.ACTIVE,
        ~Student.id.in_(students_with_payment)
    ).offset(skip).limit(limit).all()

    debtor_list = []
    for student in debtors:
        active_contract = db.query(Contract).filter(
            Contract.student_id == student.id,
            Contract.status == ContractStatus.ACTIVE
        ).first()

        debtor_list.append({
            "student_id": student.id,
            "student_name": f"{student.first_name} {student.last_name}",
            "parent_phone": student.parent_phone,
            "group": student.group.name if student.group else None,
            "monthly_fee": active_contract.final_monthly_fee if active_contract else 0,
            "contract_number": active_contract.contract_number if active_contract else None
        })

    return {
        "month": current_month,
        "year": current_year,
        "total_debtors": len(debtor_list),
        "debtors": debtor_list
    }


@router.get("/groups/{group_id}/statistics")
async def get_group_statistics(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Student count
    student_count = db.query(func.count(Student.id)).filter(
        Student.group_id == group_id,
        Student.is_active == True
    ).scalar()

    # Payment statistics for current month
    current_month = datetime.now().month
    current_year = datetime.now().year

    students_paid = db.query(func.count(func.distinct(Payment.student_id))).join(Student).filter(
        Student.group_id == group_id,
        Payment.month == current_month,
        Payment.year == current_year,
        Payment.payment_status == PaymentStatus.COMPLETED
    ).scalar()

    # Attendance statistics (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)

    total_sessions = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.group_id == group_id,
        TrainingSession.session_date >= thirty_days_ago.date()
    ).scalar()

    present_count = db.query(func.count(Attendance.id)).join(TrainingSession).filter(
        TrainingSession.group_id == group_id,
        TrainingSession.session_date >= thirty_days_ago.date(),
        Attendance.status == AttendanceStatus.PRESENT
    ).scalar()

    total_attendance_records = db.query(func.count(Attendance.id)).join(TrainingSession).filter(
        TrainingSession.group_id == group_id,
        TrainingSession.session_date >= thirty_days_ago.date()
    ).scalar()

    attendance_rate = (present_count / total_attendance_records * 100) if total_attendance_records > 0 else 0

    return {
        "group_id": group_id,
        "group_name": group.name,
        "teacher": group.teacher.full_name if group.teacher else None,
        "total_students": student_count,
        "students_paid_this_month": students_paid,
        "payment_rate": (students_paid / student_count * 100) if student_count > 0 else 0,
        "sessions_last_30_days": total_sessions,
        "attendance_rate_last_30_days": round(attendance_rate, 2)
    }


@router.get("/attendance/summary")
async def get_attendance_summary(
    start_date: datetime = None,
    end_date: datetime = None,
    group_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get attendance summary with filters"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    query = db.query(
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).join(TrainingSession).filter(
        TrainingSession.session_date >= start_date.date(),
        TrainingSession.session_date <= end_date.date()
    )

    if group_id:
        query = query.filter(TrainingSession.group_id == group_id)

    results = query.group_by(Attendance.status).all()

    summary = {status.value: 0 for status in AttendanceStatus}
    for status, count in results:
        summary[status.value] = count

    total = sum(summary.values())

    return {
        "period": {
            "start": start_date.date(),
            "end": end_date.date()
        },
        "summary": summary,
        "total_records": total
    }
