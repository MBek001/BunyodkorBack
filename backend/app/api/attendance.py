from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.attendance import Attendance, Session as TrainingSession, AttendanceStatus
from app.models.group import Group
from app.models.student import Student
from app.models.turnstile import TurnstileLog
from app.schemas.attendance import (
    SessionCreate, SessionResponse, AttendanceCreate,
    AttendanceUpdate, AttendanceResponse
)
from app.api.dependencies import get_current_user, get_current_teacher, get_current_superuser_or_admin

router = APIRouter()


# Session Management
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser_or_admin)
):
    """Create a new training session"""
    group = db.query(Group).filter(Group.id == session_data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    session = TrainingSession(**session_data.dict())
    db.add(session)
    db.commit()
    db.refresh(session)

    # Auto-create attendance records for all students in the group
    students = db.query(Student).filter(
        Student.group_id == group.id,
        Student.is_active == True
    ).all()

    for student in students:
        # Check if student entered through turnstile today
        entered_building = db.query(TurnstileLog).filter(
            TurnstileLog.student_id == student.id,
            TurnstileLog.entry_time >= session_data.session_date,
            TurnstileLog.access_granted == True
        ).first() is not None

        attendance = Attendance(
            session_id=session.id,
            student_id=student.id,
            status=AttendanceStatus.ABSENT,  # Default to absent, teacher will mark
            entered_building=entered_building
        )
        db.add(attendance)

    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    group_id: int = None,
    session_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sessions with optional filters"""
    query = db.query(TrainingSession)

    # If teacher, only show their groups' sessions
    if current_user.role == UserRole.TEACHER:
        query = query.join(Group).filter(Group.teacher_id == current_user.id)

    if group_id:
        query = query.filter(TrainingSession.group_id == group_id)
    if session_date:
        query = query.filter(TrainingSession.session_date == session_date)

    sessions = query.order_by(TrainingSession.session_date.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get session by ID"""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if teacher has access to this session
    if current_user.role == UserRole.TEACHER:
        group = db.query(Group).filter(Group.id == session.group_id).first()
        if group.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return session


@router.put("/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark session as completed"""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if teacher has access
    if current_user.role == UserRole.TEACHER:
        group = db.query(Group).filter(Group.id == session.group_id).first()
        if group.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    session.is_completed = True
    db.commit()

    return {"message": "Session marked as completed"}


# Attendance Management
@router.post("/", response_model=AttendanceResponse)
async def create_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create attendance record (usually auto-created with session)"""
    attendance = Attendance(
        **attendance_data.dict(),
        marked_by=current_user.id
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/", response_model=List[AttendanceResponse])
async def get_attendance_records(
    skip: int = 0,
    limit: int = 100,
    session_id: int = None,
    student_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance records with optional filters"""
    query = db.query(Attendance)

    if session_id:
        query = query.filter(Attendance.session_id == session_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    # If teacher, only show their sessions
    if current_user.role == UserRole.TEACHER:
        query = query.join(TrainingSession).join(Group).filter(
            Group.teacher_id == current_user.id
        )

    attendance_records = query.offset(skip).limit(limit).all()
    return attendance_records


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance record by ID"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update attendance record (mark as present/absent/late/excused)"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    # Check if teacher has access
    if current_user.role == UserRole.TEACHER:
        session = db.query(TrainingSession).filter(
            TrainingSession.id == attendance.session_id
        ).first()
        group = db.query(Group).filter(Group.id == session.group_id).first()
        if group.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    for field, value in attendance_data.dict(exclude_unset=True).items():
        setattr(attendance, field, value)

    attendance.marked_by = current_user.id
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/student/{student_id}/history")
async def get_student_attendance_history(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance history for a specific student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    attendance_records = db.query(Attendance).join(TrainingSession).filter(
        Attendance.student_id == student_id
    ).order_by(TrainingSession.session_date.desc()).offset(skip).limit(limit).all()

    return attendance_records
