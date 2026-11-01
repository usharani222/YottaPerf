from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Date, DateTime, Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class ReviewCycle(Base):
    __tablename__ = "review_cycles"

    cycle_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # CYCLE-2026-H1
    cycle_name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    submission_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    stage: Mapped[str] = mapped_column(String(50), default="UPCOMING", nullable=False)  # UPCOMING, OPEN, EVALUATION, CLOSED, ARCHIVED
    
    # Configurable scoring weights
    goal_weight: Mapped[float] = mapped_column(Numeric(5, 2), default=50.00, nullable=False)
    competency_weight: Mapped[float] = mapped_column(Numeric(5, 2), default=30.00, nullable=False)
    feedback_weight: Mapped[float] = mapped_column(Numeric(5, 2), default=20.00, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="review_cycle")
    check_ins: Mapped[List["CheckIn"]] = relationship("CheckIn", back_populates="review_cycle")
    feedbacks: Mapped[List["Feedback"]] = relationship("Feedback", back_populates="review_cycle")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="review_cycle")
    permissions: Mapped[List["ReviewPermission"]] = relationship("ReviewPermission", back_populates="review_cycle")

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="chk_cycle_dates"),
        CheckConstraint("stage IN ('UPCOMING', 'OPEN', 'EVALUATION', 'CLOSED', 'ARCHIVED')", name="chk_cycle_stage"),
    )
