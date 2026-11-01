import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.services.cycle_service import ReviewCycleService, ClosedCycleModificationException
from backend.app.models.audit import AuditEvent
from backend.app.models.development_plan import DevelopmentPlan


def test_14_closed_review_cycle_modification_rejection(client: TestClient, admin_headers: dict):
    """TEST 14: Modification to a CLOSED review cycle must be rejected without authorized correction."""
    # Attempt to create a goal in closed cycle CYCLE-2025-H2
    payload = {
        "goal_id": "GOAL-CLOSED-FAIL",
        "employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2025-H2",  # CLOSED cycle!
        "title": "Unauthorized Objective",
        "category": "TECHNICAL",
        "start_date": "2025-07-01",
        "due_date": "2025-12-31",
        "is_admin_correction": False
    }
    response = client.post("/api/goals", json=payload, headers=admin_headers)
    assert response.status_code == 403
    assert "closed" in response.json()["detail"].lower()


def test_15_audit_history_creation(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 15: Immutable AuditEvent is created when administrative corrections are applied."""
    # Create goal with explicit administrative correction
    payload = {
        "goal_id": "GOAL-CLOSED-CORRECTED",
        "employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2025-H2",
        "title": "Authorized Late Correction",
        "category": "TECHNICAL",
        "start_date": "2025-07-01",
        "due_date": "2025-12-31",
        "is_admin_correction": True,
        "correction_reason": "Audit Compliance Late Adjustment Ticket #884"
    }
    response = client.post("/api/goals", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text

    # Verify AuditEvent exists
    audit = db_session.execute(
        select(AuditEvent).where(
            AuditEvent.review_cycle_id == "CYCLE-2025-H2",
            AuditEvent.operation_type == "CORRECTION"
        )
    ).scalar_one_or_none()
    assert audit is not None
    assert "Ticket #884" in audit.reason


def test_16_development_plan_approval(client: TestClient, admin_headers: dict):
    """TEST 16: Development plan creation and manager approval workflow."""
    plan_payload = {
        "plan_id": "DP-TEST-001",
        "employee_id": "EMP-000991",
        "competency_id": "COMP-TECH-01",
        "current_level": "Intermediate",
        "target_level": "Senior Expert",
        "recommended_action": "Complete advanced system architecture workshops.",
        "start_date": "2026-03-01",
        "target_completion_date": "2026-09-30"
    }
    create_res = client.post("/api/development-plans", json=plan_payload, headers=admin_headers)
    assert create_res.status_code == 201, create_res.text
    plan_data = create_res.json()
    assert plan_data["approval_status"] == "PENDING"

    # Manager approves
    appr_payload = {
        "decision": "APPROVED",
        "approval_role": "MANAGER",
        "comments": "Approved. Excellent growth targets for H2."
    }
    appr_res = client.post("/api/development-plans/DP-TEST-001/approve", json=appr_payload, headers=admin_headers)
    assert appr_res.status_code == 200, appr_res.text
    updated_plan = appr_res.json()
    assert updated_plan["approval_status"] == "APPROVED"
