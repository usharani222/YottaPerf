from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Date, DateTime, Numeric, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee_roles: Mapped[List["EmployeeRole"]] = relationship(
        "EmployeeRole", back_populates="role", cascade="all, delete-orphan"
    )


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="employee_roles")


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # EMP-000001
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    job_level: Mapped[str] = mapped_column(String(20), nullable=False)
    manager_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Hierarchy self-reference
    direct_reports: Mapped[List["Employee"]] = relationship(
        "Employee", back_populates="manager", foreign_keys=[manager_id]
    )
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", back_populates="direct_reports", remote_side=[employee_id], foreign_keys=[manager_id]
    )

    # Account and Role relationships
    user_account: Mapped[Optional["UserAccount"]] = relationship(
        "UserAccount", back_populates="employee", uselist=False, cascade="all, delete-orphan"
    )
    roles: Mapped[List["EmployeeRole"]] = relationship(
        "EmployeeRole", back_populates="employee", cascade="all, delete-orphan"
    )
    manager_profile: Mapped[Optional["Manager"]] = relationship(
        "Manager", back_populates="employee", uselist=False
    )
    manager_history: Mapped[List["EmployeeManagerHistory"]] = relationship(
        "EmployeeManagerHistory", back_populates="employee", foreign_keys="EmployeeManagerHistory.employee_id"
    )

    # Goals, Check-ins, Feedbacks, Reviews, Development Plans
    goals: Mapped[List["Goal"]] = relationship(
        "Goal", back_populates="employee", foreign_keys="Goal.employee_id"
    )
    check_ins: Mapped[List["CheckIn"]] = relationship(
        "CheckIn", back_populates="employee"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="employee"
    )
    development_plans: Mapped[List["DevelopmentPlan"]] = relationship(
        "DevelopmentPlan", back_populates="employee"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserAccount(Base):
    __tablename__ = "user_accounts"

    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # USR-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="user_account")


class Manager(Base):
    __tablename__ = "managers"

    manager_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # MGR-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    management_level: Mapped[str] = mapped_column(String(50), nullable=False)
    budget_authority: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped["Employee"] = relationship("Employee", back_populates="manager_profile")


class EmployeeManagerHistory(Base):
    __tablename__ = "employee_manager_histories"

    history_id: Mapped[str] = mapped_column(String(32), primary_key=True)  # EMH-000001
    employee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    manager_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False
    )
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    transfer_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="manager_history", foreign_keys=[employee_id]
    )
    manager: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[manager_id]
    )
