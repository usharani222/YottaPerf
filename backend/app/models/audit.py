from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import (
    String, DateTime, ForeignKey, JSON, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # AUD-000001
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True
    )
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # CREATE, UPDATE, DELETE, TRANSITION, CORRECTION
    old_values: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    review_cycle_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("review_cycles.cycle_id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    actor: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[actor_id])
    review_cycle: Mapped[Optional["ReviewCycle"]] = relationship("ReviewCycle")

    __table_args__ = (
        CheckConstraint("operation_type IN ('CREATE', 'UPDATE', 'DELETE', 'TRANSITION', 'CORRECTION')", name="chk_audit_op"),
    )
