from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Date, DateTime, Numeric, ForeignKey, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # FB-000001
    subject_employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    reviewer_employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    review_cycle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)  # SELF, MANAGER, PEER
    competency_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("competencies.competency_id", ondelete="RESTRICT"), nullable=False
    )
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)  # 1.00 to 5.00
    comments: Mapped[str] = mapped_column(Text, nullable=False)
    submission_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False)  # DRAFT, SUBMITTED, REVISED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    subject_employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[subject_employee_id])
    reviewer_employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[reviewer_employee_id])
    review_cycle: Mapped["ReviewCycle"] = relationship("ReviewCycle", back_populates="feedbacks")
    competency: Mapped["Competency"] = relationship("Competency", back_populates="feedbacks")
    evidence_links: Mapped[List["FeedbackEvidence"]] = relationship(
        "FeedbackEvidence", back_populates="feedback", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("feedback_type IN ('SELF', 'MANAGER', 'PEER')", name="chk_fb_type"),
        CheckConstraint("rating >= 1.00 AND rating <= 5.00", name="chk_fb_rating"),
        CheckConstraint("status IN ('DRAFT', 'SUBMITTED', 'REVISED')", name="chk_fb_status"),
    )


class FeedbackEvidence(Base):
    __tablename__ = "feedback_evidence"

    feedback_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("feedbacks.feedback_id", ondelete="CASCADE"), primary_key=True
    )
    evidence_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("evidences.evidence_id", ondelete="CASCADE"), primary_key=True
    )
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="evidence_links")
    evidence: Mapped["Evidence"] = relationship("Evidence", back_populates="feedback_evidence")


class ReviewPermission(Base):
    __tablename__ = "review_permissions"

    permission_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # RP-000001
    review_cycle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="CASCADE"), nullable=False
    )
    subject_employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False
    )
    reviewer_employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String(30), nullable=False)  # PEER, CROSS_FUNCTIONAL
    granted_by: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    review_cycle: Mapped["ReviewCycle"] = relationship("ReviewCycle", back_populates="permissions")
    subject: Mapped["Employee"] = relationship("Employee", foreign_keys=[subject_employee_id])
    reviewer: Mapped["Employee"] = relationship("Employee", foreign_keys=[reviewer_employee_id])
    granter: Mapped["Employee"] = relationship("Employee", foreign_keys=[granted_by])

    __table_args__ = (
        UniqueConstraint("review_cycle_id", "subject_employee_id", "reviewer_employee_id", name="uq_cycle_subject_reviewer"),
    )
