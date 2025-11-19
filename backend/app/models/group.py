from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    schedule = Column(String, nullable=True)  # JSON string: {"monday": "10:00-12:00", "wednesday": "10:00-12:00"}
    max_students = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("User", back_populates="teacher_groups")
    students = relationship("Student", back_populates="group")
    sessions = relationship("Session", back_populates="group", cascade="all, delete-orphan")
