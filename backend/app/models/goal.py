from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Date, DateTime, Numeric, ForeignKey, Text, CheckConstraint, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Goal(Base):
    __tablename__ = "goals"

    goal_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # GOAL-EMP-000001-001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    review_cycle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # TECHNICAL, LEADERSHIP, DELIVERY, etc.
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(5, 2), default=1.00, nullable=False)
    calculated_progress: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, SUBMITTED, ACTIVE, COMPLETED, CANCELLED
    created_by: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    approved_by: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="goals")
    creator: Mapped["Employee"] = relationship("Employee", foreign_keys=[created_by])
    approver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[approved_by])
    review_cycle: Mapped["ReviewCycle"] = relationship("ReviewCycle", back_populates="goals")
    key_results: Mapped[List["KeyResult"]] = relationship(
        "KeyResult", back_populates="goal", cascade="all, delete-orphan"
    )
    history: Mapped[List["GoalHistory"]] = relationship(
        "GoalHistory", back_populates="goal", cascade="all, delete-orphan"
    )
    check_ins: Mapped[List["CheckIn"]] = relationship("CheckIn", back_populates="goal")

    __table_args__ = (
        CheckConstraint("due_date >= start_date", name="chk_goal_dates"),
        CheckConstraint("weight > 0", name="chk_goal_weight"),
        CheckConstraint("status IN ('DRAFT', 'SUBMITTED', 'ACTIVE', 'COMPLETED', 'CANCELLED')", name="chk_goal_status"),
        CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_goal_priority"),
    )


class KeyResult(Base):
    __tablename__ = "key_results"

    key_result_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # KR-GOAL-EMP-000001-001-01
    goal_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False)
    metric_direction: Mapped[str] = mapped_column(String(20), default="INCREASING", nullable=False)  # INCREASING, DECREASING
    baseline_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    target_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    current_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # PERCENT, COUNT, USD, DAYS, etc.
    weight: Mapped[float] = mapped_column(Numeric(5, 2), default=1.00, nullable=False)
    progress_percentage: Mapped[float] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ON_TRACK", nullable=False)  # ON_TRACK, AT_RISK, BEHIND, ACHIEVED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped["Goal"] = relationship("Goal", back_populates="key_results")

    __table_args__ = (
        CheckConstraint("metric_direction IN ('INCREASING', 'DECREASING')", name="chk_kr_direction"),
        CheckConstraint("weight > 0", name="chk_kr_weight"),
        CheckConstraint("status IN ('ON_TRACK', 'AT_RISK', 'BEHIND', 'ACHIEVED')", name="chk_kr_status"),
    )


class GoalHistory(Base):
    __tablename__ = "goal_histories"

    history_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # GH-000001
    goal_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    calculated_progress: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    changed_by: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    change_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped["Goal"] = relationship("Goal", back_populates="history")
    author: Mapped["Employee"] = relationship("Employee", foreign_keys=[changed_by])
