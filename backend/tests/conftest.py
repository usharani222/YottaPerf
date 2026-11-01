import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment SQLite database
os.environ["DATABASE_URL"] = "sqlite:///test_yottaperf.db"

from backend.app.core.config import settings
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.main import app
from backend.app.models import (
    Role, EmployeeRole, Employee, UserAccount, Manager, ReviewCycle, Competency
)

TEST_DB_URL = "sqlite:///test_yottaperf.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Pre-seed basic roles
    db = TestingSessionLocal()
    roles = [
        Role(role_id="ROLE-EMP", name="EMPLOYEE", description="Employee role"),
        Role(role_id="ROLE-MGR", name="MANAGER", description="Manager role"),
        Role(role_id="ROLE-HR", name="HR_PARTNER", description="HR role"),
        Role(role_id="ROLE-OPS", name="IT_OPS", description="Ops role"),
        Role(role_id="ROLE-ADM", name="ADMIN", description="Admin role"),
    ]
    for r in roles:
        db.merge(r)

    # Pre-seed competencies
    comp = Competency(
        competency_id="COMP-TECH-01",
        category="Technical Skills",
        name="Software Architecture",
        description="Architecture competence"
    )
    db.merge(comp)

    # Pre-seed review cycles
    c_open = ReviewCycle(
        cycle_id="CYCLE-2026-H1",
        cycle_name="2026 H1 Review",
        start_date=settings.REFERENCE_DATE,
        end_date=settings.REFERENCE_DATE,
        submission_deadline=settings.REFERENCE_DATE,
        stage="OPEN",
        goal_weight=50.0,
        competency_weight=30.0,
        feedback_weight=20.0
    )
    from datetime import date
    c_open.start_date = date(2026, 1, 1)
    c_open.end_date = date(2026, 6, 30)
    c_open.submission_deadline = date(2026, 6, 15)

    c_closed = ReviewCycle(
        cycle_id="CYCLE-2025-H2",
        cycle_name="2025 H2 Review",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 12, 31),
        submission_deadline=date(2025, 12, 15),
        stage="CLOSED",
        goal_weight=50.0,
        competency_weight=30.0,
        feedback_weight=20.0
    )
    db.merge(c_open)
    db.merge(c_closed)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_yottaperf.db"):
        os.remove("test_yottaperf.db")


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(db_session: Session) -> dict:
    emp = Employee(
        employee_id="EMP-TEST-ADMIN",
        first_name="Admin",
        last_name="User",
        email="admin@test.internal",
        department="Operations",
        job_title="System Administrator",
        job_level="EXEC",
        hire_date=settings.REFERENCE_DATE
    )
    from datetime import date
    emp.hire_date = date(2021, 1, 1)
    db_session.merge(emp)

    user = UserAccount(
        user_id="USR-TEST-ADMIN",
        employee_id="EMP-TEST-ADMIN",
        username="admin_test",
        email="admin@test.internal",
        hashed_password="hashed_test_pwd",
        is_active=True
    )
    db_session.merge(user)

    er = EmployeeRole(employee_id="EMP-TEST-ADMIN", role_id="ROLE-ADM")
    db_session.merge(er)
    db_session.commit()

    token = create_access_token(
        subject="USR-TEST-ADMIN",
        claims={"employee_id": "EMP-TEST-ADMIN", "username": "admin_test", "roles": ["ADMIN"]}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_headers(db_session: Session) -> dict:
    from datetime import date
    emp = Employee(
        employee_id="EMP-TEST-EMP1",
        first_name="Alice",
        last_name="Engineer",
        email="alice@test.internal",
        department="Engineering",
        job_title="Software Engineer",
        job_level="IC3",
        hire_date=date(2023, 1, 15)
    )
    db_session.merge(emp)

    user = UserAccount(
        user_id="USR-TEST-EMP1",
        employee_id="EMP-TEST-EMP1",
        username="alice_test",
        email="alice@test.internal",
        hashed_password="hashed_pwd",
        is_active=True
    )
    db_session.merge(user)

    er = EmployeeRole(employee_id="EMP-TEST-EMP1", role_id="ROLE-EMP")
    db_session.merge(er)
    db_session.commit()

    token = create_access_token(
        subject="USR-TEST-EMP1",
        claims={"employee_id": "EMP-TEST-EMP1", "username": "alice_test", "roles": ["EMPLOYEE"]}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_employee_headers(db_session: Session) -> dict:
    from datetime import date
    emp = Employee(
        employee_id="EMP-TEST-EMP2",
        first_name="Bob",
        last_name="Designer",
        email="bob@test.internal",
        department="Product",
        job_title="Product Designer",
        job_level="IC3",
        hire_date=date(2023, 3, 1)
    )
    db_session.merge(emp)

    user = UserAccount(
        user_id="USR-TEST-EMP2",
        employee_id="EMP-TEST-EMP2",
        username="bob_test",
        email="bob@test.internal",
        hashed_password="hashed_pwd",
        is_active=True
    )
    db_session.merge(user)

    er = EmployeeRole(employee_id="EMP-TEST-EMP2", role_id="ROLE-EMP")
    db_session.merge(er)
    db_session.commit()

    token = create_access_token(
        subject="USR-TEST-EMP2",
        claims={"employee_id": "EMP-TEST-EMP2", "username": "bob_test", "roles": ["EMPLOYEE"]}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_headers(db_session: Session) -> dict:
    from datetime import date
    emp = Employee(
        employee_id="EMP-TEST-MGR1",
        first_name="Carol",
        last_name="Manager",
        email="carol@test.internal",
        department="Engineering",
        job_title="Engineering Manager",
        job_level="MGR",
        hire_date=date(2022, 1, 1)
    )
    db_session.merge(emp)

    mgr = Manager(
        manager_id="MGR-TEST-001",
        employee_id="EMP-TEST-MGR1",
        department="Engineering",
        team_size=5
    )
    db_session.merge(mgr)

    user = UserAccount(
        user_id="USR-TEST-MGR1",
        employee_id="EMP-TEST-MGR1",
        username="carol_test",
        email="carol@test.internal",
        hashed_password="hashed_pwd",
        is_active=True
    )
    db_session.merge(user)

    er = EmployeeRole(employee_id="EMP-TEST-MGR1", role_id="ROLE-MGR")
    db_session.merge(er)
    db_session.commit()

    token = create_access_token(
        subject="USR-TEST-MGR1",
        claims={"employee_id": "EMP-TEST-MGR1", "username": "carol_test", "roles": ["MANAGER"]}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hr_headers(db_session: Session) -> dict:
    from datetime import date
    emp = Employee(
        employee_id="EMP-TEST-HR1",
        first_name="Dana",
        last_name="Partner",
        email="dana@test.internal",
        department="Human Resources",
        job_title="HR Business Partner",
        job_level="MGR",
        hire_date=date(2021, 6, 1)
    )
    db_session.merge(emp)

    user = UserAccount(
        user_id="USR-TEST-HR1",
        employee_id="EMP-TEST-HR1",
        username="dana_test",
        email="dana@test.internal",
        hashed_password="hashed_pwd",
        is_active=True
    )
    db_session.merge(user)

    er = EmployeeRole(employee_id="EMP-TEST-HR1", role_id="ROLE-HR")
    db_session.merge(er)
    db_session.commit()

    token = create_access_token(
        subject="USR-TEST-HR1",
        claims={"employee_id": "EMP-TEST-HR1", "username": "dana_test", "roles": ["HR_PARTNER"]}
    )
    return {"Authorization": f"Bearer {token}"}

