from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, DateTime, Numeric, ForeignKey, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # REV-2026-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    review_cycle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    goal_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    competency_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    feedback_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    rating_category: Mapped[str] = mapped_column(
        String(50), default="MEETS_EXPECTATIONS", nullable=False
    )  # NEEDS_IMPROVEMENT, MEETS_EXPECTATIONS, EXCEEDS_EXPECTATIONS, OUTSTANDING
    stage: Mapped[str] = mapped_column(
        String(50), default="DRAFT", nullable=False, index=True
    )  # DRAFT, SELF_REVIEW_PENDING, MANAGER_REVIEW_PENDING, HR_REVIEW_PENDING, APPROVED, COMPLETED, REJECTED, RETURNED_FOR_REVISION, INCOMPLETE
    
    self_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hr_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    self_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    manager_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    hr_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="reviews")
    review_cycle: Mapped["ReviewCycle"] = relationship("ReviewCycle", back_populates="reviews")
    history: Mapped[List["ReviewHistory"]] = relationship(
        "ReviewHistory", back_populates="review", cascade="all, delete-orphan"
    )
    development_plans: Mapped[List["DevelopmentPlan"]] = relationship(
        "DevelopmentPlan", back_populates="originating_review"
    )

    __table_args__ = (
        UniqueConstraint("employee_id", "review_cycle_id", name="uq_emp_cycle_review"),
        CheckConstraint(
            "stage IN ('DRAFT', 'SELF_REVIEW_PENDING', 'MANAGER_REVIEW_PENDING', 'HR_REVIEW_PENDING', 'APPROVED', 'COMPLETED', 'REJECTED', 'RETURNED_FOR_REVISION', 'INCOMPLETE')",
            name="chk_rev_stage"
        ),
        CheckConstraint(
            "rating_category IN ('NEEDS_IMPROVEMENT', 'MEETS_EXPECTATIONS', 'EXCEEDS_EXPECTATIONS', 'OUTSTANDING')",
            name="chk_rev_rating"
        ),
    )


class ReviewHistory(Base):
    __tablename__ = "review_histories"

    history_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # RH-000001
    review_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("reviews.review_id", ondelete="CASCADE"), nullable=False, index=True
    )
    previous_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    new_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    review: Mapped["Review"] = relationship("Review", back_populates="history")
    actor: Mapped["Employee"] = relationship("Employee", foreign_keys=[changed_by])
