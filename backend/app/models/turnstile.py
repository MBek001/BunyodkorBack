from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TurnstileLog(Base):
    __tablename__ = "turnstile_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    turnstile_id = Column(String, nullable=True)  # Which turnstile device
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    access_granted = Column(Boolean, nullable=False)
    payment_verified = Column(Boolean, default=False)
    face_match_confidence = Column(Integer, nullable=True)  # 0-100
    notes = Column(String, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="turnstile_logs")
