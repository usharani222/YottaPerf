import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.services.feedback_service import FeedbackService, InvalidReviewerException
from backend.app.services.review_service import ReviewService, ReviewPermissionException
from backend.app.models.employee import Employee, UserAccount, EmployeeRole
from backend.app.models.goal import Goal
from backend.app.core.security import create_access_token


def test_10_reviewer_relationship_validation(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 10: Reviewer relationship eligibility validation."""
    fb_svc = FeedbackService(db_session)
    
    # Alice (EMP-000991) and Bob (EMP-000992) are in Engineering
    alice = Employee(
        employee_id="EMP-000991",
        first_name="Alice",
        last_name="Smith",
        email="alice.smith991@yottaperf.internal",
        department="Engineering",
        job_title="Software Engineer",
        job_level="IC3",
        manager_id="EMP-000992",
        hire_date=date(2024, 1, 15)
    )
    bob = Employee(
        employee_id="EMP-000992",
        first_name="Bob",
        last_name="Manager",
        email="bob.manager992@yottaperf.internal",
        department="Engineering",
        job_title="Engineering Lead",
        job_level="M2",
        hire_date=date(2022, 1, 10)
    )
    charlie = Employee(
        employee_id="EMP-000993",
        first_name="Charlie",
        last_name="Sales",
        email="charlie.sales993@yottaperf.internal",
        department="Sales",
        job_title="Account Executive",
        job_level="IC2",
        hire_date=date(2023, 2, 1)
    )
    db_session.merge(alice)
    db_session.merge(bob)
    db_session.merge(charlie)
    db_session.commit()

    # Valid: Bob is Alice's manager -> MANAGER relationship valid
    assert fb_svc.validate_reviewer_relationship("EMP-000991", "EMP-000992", "MANAGER", "CYCLE-2026-H1") is True

    # Invalid: Charlie has no relationship to Alice -> PEER relationship invalid
    assert fb_svc.validate_reviewer_relationship("EMP-000991", "EMP-000993", "PEER", "CYCLE-2026-H1") is False


def test_11_conflicting_feedback_handling(db_session: Session, client: TestClient):
    """TEST 11: Non-destructive handling of divergent feedback."""
    # Ensure Alice and Bob exist with user accounts for token authentication
    for emp_id, uname, roles in [
        ("EMP-000991", "alice_991", ["EMPLOYEE"]),
        ("EMP-000992", "bob_992", ["MANAGER"])
    ]:
        user = UserAccount(
            user_id=f"USR-{emp_id}",
            employee_id=emp_id,
            username=uname,
            email=f"{uname}@test.internal",
            hashed_password="hash",
            is_active=True
        )
        db_session.merge(user)
        for r in roles:
            er = EmployeeRole(employee_id=emp_id, role_id=f"ROLE-{'EMP' if r=='EMPLOYEE' else 'MGR'}")
            db_session.merge(er)
    db_session.commit()

    alice_token = create_access_token("USR-EMP-000991", claims={"employee_id": "EMP-000991", "roles": ["EMPLOYEE"]})
    bob_token = create_access_token("USR-EMP-000992", claims={"employee_id": "EMP-000992", "roles": ["MANAGER"]})

    # 1. Alice submits Self Feedback (rating 4.5)
    fb1_payload = {
        "feedback_id": "FB-TEST-001",
        "subject_employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2026-H1",
        "feedback_type": "SELF",
        "competency_id": "COMP-TECH-01",
        "rating": 4.5,
        "comments": "Self: High technical contribution."
    }
    res1 = client.post("/api/feedback", json=fb1_payload, headers={"Authorization": f"Bearer {alice_token}"})
    assert res1.status_code == 201, res1.text

    # 2. Bob submits Manager Feedback on same competency with different rating (3.0)
    fb2_payload = {
        "feedback_id": "FB-TEST-002",
        "subject_employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2026-H1",
        "feedback_type": "MANAGER",
        "competency_id": "COMP-TECH-01",
        "rating": 3.0,
        "comments": "Manager: Solid delivery but needs broader design documentation."
    }
    res2 = client.post("/api/feedback", json=fb2_payload, headers={"Authorization": f"Bearer {bob_token}"})
    assert res2.status_code == 201, res2.text

    # Both records must coexist without overwriting
    feedbacks_res = client.get("/api/feedback?subject_employee_id=EMP-000991", headers={"Authorization": f"Bearer {alice_token}"})
    assert feedbacks_res.status_code == 200
    fbs = feedbacks_res.json()
    assert len(fbs) >= 2
    ratings = [f["rating"] for f in fbs]
    assert 4.5 in ratings and 3.0 in ratings


def test_12_review_score_calculation(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 12: Review score calculation from actual contributing records."""
    # Ensure goal with progress exists for Alice
    goal = Goal(
        goal_id="GOAL-ALICE-TEST",
        employee_id="EMP-000991",
        review_cycle_id="CYCLE-2026-H1",
        title="Distributed Caching Layer",
        category="TECHNICAL",
        priority="HIGH",
        start_date=date(2026, 1, 1),
        due_date=date(2026, 6, 30),
        weight=1.0,
        calculated_progress=87.5,
        status="ACTIVE",
        created_by="EMP-000991"
    )
    db_session.merge(goal)
    db_session.commit()

    rev_payload = {
        "review_id": "REV-TEST-001",
        "employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2026-H1"
    }
    response = client.post("/api/reviews", json=rev_payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    rev = response.json()
    
    # Goal score should reflect Goal calculated_progress (87.5%)
    assert rev["goal_score"] == 87.5
    # Final score calculated as (goal*0.5 + comp*0.3 + fb*0.2)
    expected_score = round(
        (87.5 * 0.50) + (rev["competency_score"] * 0.30) + (rev["feedback_score"] * 0.20),
        2
    )
    assert abs(rev["final_score"] - expected_score) <= 0.05
    assert rev["stage"] == "DRAFT"


def test_13_review_approval_permissions(db_session: Session):
    """TEST 13: Security rule: Employees cannot approve their own performance reviews."""
    rev_svc = ReviewService(db_session)
    
    # Employee attempting to approve their own review must raise ReviewPermissionException
    with pytest.raises(ReviewPermissionException):
        rev_svc.transition_stage(
            review_id="REV-TEST-001",
            target_stage="APPROVED",
            actor_id="EMP-000991"  # Alice trying to approve herself!
        )
