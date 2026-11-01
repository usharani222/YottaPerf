from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, DateTime, ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # ANO-000001
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    affected_entity: Mapped[str] = mapped_column(String(50), nullable=False)
    affected_record_id: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detection_status: Mapped[str] = mapped_column(
        String(30), default="DETECTED", nullable=False, index=True
    )  # DETECTED, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    ground_truth_label: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_resolution: Mapped[str] = mapped_column(Text, nullable=False)
    detection_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    resolver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[resolved_by])

    __table_args__ = (
        CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_ano_severity"),
        CheckConstraint("detection_status IN ('DETECTED', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE')", name="chk_ano_status"),
    )
