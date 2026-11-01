from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Date, DateTime, Numeric, ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class CheckIn(Base):
    __tablename__ = "check_ins"

    check_in_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # CHK-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    goal_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("goals.goal_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    review_cycle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="RESTRICT"), nullable=False
    )
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)
    progress_update: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    employee_comments: Mapped[str] = mapped_column(Text, nullable=False)
    manager_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blockers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="check_ins")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="check_ins")
    review_cycle: Mapped["ReviewCycle"] = relationship("ReviewCycle", back_populates="check_ins")
    evidences: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="check_in")


class Evidence(Base):
    __tablename__ = "evidences"

    evidence_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # EVD-000001
    check_in_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("check_ins.check_in_id", ondelete="SET NULL"), nullable=True, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CODE_PR, METRIC_DASHBOARD, CERTIFICATION, etc.
    reference_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    uploaded_date: Mapped[date] = mapped_column(Date, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(30), default="VERIFIED", nullable=False)  # VERIFIED, PENDING_REVIEW, REJECTED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    check_in: Mapped[Optional["CheckIn"]] = relationship("CheckIn", back_populates="evidences")
    uploader: Mapped["Employee"] = relationship("Employee", foreign_keys=[uploaded_by])
    feedback_evidence: Mapped[List["FeedbackEvidence"]] = relationship(
        "FeedbackEvidence", back_populates="evidence", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("verification_status IN ('VERIFIED', 'PENDING_REVIEW', 'REJECTED')", name="chk_evd_status"),
    )
