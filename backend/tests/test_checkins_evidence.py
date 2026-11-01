from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.employee import Employee
from backend.app.models.goal import Goal


def test_08_and_09_checkin_creation_and_evidence_linking(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 8 & 9: Periodic check-in submission and evidence artifact linking."""
    # Ensure prerequisite employee and goal exist
    emp = Employee(
        employee_id="EMP-CHK-TEST",
        first_name="David",
        last_name="Test",
        email="david.test@yottaperf.internal",
        department="Engineering",
        job_title="Software Engineer",
        job_level="IC2",
        hire_date=date(2023, 1, 1)
    )
    db_session.merge(emp)

    goal = Goal(
        goal_id="GOAL-CHK-TEST",
        employee_id="EMP-CHK-TEST",
        review_cycle_id="CYCLE-2026-H1",
        title="CheckIn Goal",
        category="TECHNICAL",
        priority="MEDIUM",
        start_date=date(2026, 1, 1),
        due_date=date(2026, 6, 30),
        weight=1.0,
        calculated_progress=50.0,
        status="ACTIVE",
        created_by="EMP-CHK-TEST"
    )
    db_session.merge(goal)
    db_session.commit()

    payload = {
        "check_in_id": "CHK-TEST-001",
        "employee_id": "EMP-CHK-TEST",
        "goal_id": "GOAL-CHK-TEST",
        "review_cycle_id": "CYCLE-2026-H1",
        "check_in_date": "2026-03-15",
        "progress_update": 50.0,
        "employee_comments": "Implemented high-throughput clustering and benchmarked throughput.",
        "manager_comments": "Benchmark numbers look solid.",
        "blockers": "None",
        "next_steps": "Staging rollout.",
        "evidence_reference_url": "https://github.com/usharani222/YottaPerf/pull/42",
        "evidence_type": "CODE_PR",
        "evidence_description": "PR #42 implements distributed Redis clustering."
    }
    response = client.post("/api/check-ins", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["check_in_id"] == "CHK-TEST-001"
    assert len(data["evidences"]) == 1
    evd = data["evidences"][0]
    assert evd["evidence_type"] == "CODE_PR"
    assert evd["verification_status"] == "VERIFIED"
    assert "PR #42" in evd["description"]
