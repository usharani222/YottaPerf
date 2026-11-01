from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Competency(Base):
    __tablename__ = "competencies"

    competency_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # COMP-001
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Technical Skills, Communication, etc.
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    feedbacks: Mapped[List["Feedback"]] = relationship("Feedback", back_populates="competency")
    development_plans: Mapped[List["DevelopmentPlan"]] = relationship("DevelopmentPlan", back_populates="competency")
