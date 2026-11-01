from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Date, DateTime, ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class DevelopmentPlan(Base):
    __tablename__ = "development_plans"

    plan_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # DP-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    review_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("reviews.review_id", ondelete="SET NULL"), nullable=True
    )
    competency_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("competencies.competency_id", ondelete="RESTRICT"), nullable=False
    )
    current_level: Mapped[str] = mapped_column(String(50), nullable=False)
    target_level: Mapped[str] = mapped_column(String(50), nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    learning_resources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="IN_PROGRESS", nullable=False
    )  # NOT_STARTED, IN_PROGRESS, COMPLETED, CANCELLED
    approval_status: Mapped[str] = mapped_column(
        String(30), default="PENDING", nullable=False
    )  # PENDING, APPROVED, REJECTED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="development_plans")
    originating_review: Mapped[Optional["Review"]] = relationship("Review", back_populates="development_plans")
    competency: Mapped["Competency"] = relationship("Competency", back_populates="development_plans")
    activities: Mapped[List["DevelopmentActivity"]] = relationship(
        "DevelopmentActivity", back_populates="plan", cascade="all, delete-orphan"
    )
    approvals: Mapped[List["DevelopmentPlanApproval"]] = relationship(
        "DevelopmentPlanApproval", back_populates="plan", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("target_completion_date >= start_date", name="chk_dp_dates"),
        CheckConstraint("status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name="chk_dp_status"),
        CheckConstraint("approval_status IN ('PENDING', 'APPROVED', 'REJECTED')", name="chk_dp_approval"),
    )


class DevelopmentActivity(Base):
    __tablename__ = "development_activities"

    activity_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # DA-000001
    plan_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("development_plans.plan_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # COURSE, WORKSHOP, MENTORING, PROJECT
    resource_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="NOT_STARTED", nullable=False)  # NOT_STARTED, IN_PROGRESS, COMPLETED
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    plan: Mapped["DevelopmentPlan"] = relationship("DevelopmentPlan", back_populates="activities")

    __table_args__ = (
        CheckConstraint("status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')", name="chk_da_status"),
    )


class DevelopmentPlanApproval(Base):
    __tablename__ = "development_plan_approvals"

    approval_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # DPA-000001
    plan_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("development_plans.plan_id", ondelete="CASCADE"), nullable=False
    )
    approver_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    approval_role: Mapped[str] = mapped_column(String(30), nullable=False)  # MANAGER, HR_PARTNER
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # APPROVED, REJECTED, REQUESTED_CHANGES
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    plan: Mapped["DevelopmentPlan"] = relationship("DevelopmentPlan", back_populates="approvals")
    approver: Mapped["Employee"] = relationship("Employee", foreign_keys=[approver_id])

    __table_args__ = (
        CheckConstraint("decision IN ('APPROVED', 'REJECTED', 'REQUESTED_CHANGES')", name="chk_dpa_decision"),
    )
