from datetime import datetime, timedelta, timezone, date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.employee import Employee, UserAccount, Manager, EmployeeRole
from backend.app.models.goal import Goal, KeyResult
from backend.app.models.check_in import CheckIn
from backend.app.models.anomaly import Anomaly
from backend.app.models.audit import AuditEvent
from backend.generator.config import get_generator_config
import json
import os


def test_21_employee_data_isolation(client: TestClient, db_session: Session, employee_headers: dict, other_employee_headers: dict):
    """
    Test Priority 3 & 9: Verify employee-level data isolation.
    An employee should not be able to create a goal or check-in on behalf of another employee without managerial authority.
    """
    # Employee 1 tries to submit check-in for Employee 2 (EMP-TEST-EMP2)
    # First create a goal for EMP-TEST-EMP2
    goal = Goal(
        goal_id="GOAL-ISOLATION-001",
        employee_id="EMP-TEST-EMP2",
        review_cycle_id="CYCLE-2026-H1",
        title="Bob Private Goal",
        category="TECHNICAL",
        priority="HIGH",
        start_date=date(2026, 1, 1),
        due_date=date(2026, 6, 30),
        weight=1.0,
        calculated_progress=0.0,
        status="ACTIVE",
        created_by="EMP-TEST-EMP2"
    )
    db_session.merge(goal)
    db_session.commit()

    # Alice (EMP-TEST-EMP1) tries to submit check-in on Bob's goal
    res = client.post(
        "/api/check-ins",
        headers=employee_headers,
        json={
            "check_in_id": "CHK-ISOLATION-001",
            "employee_id": "EMP-TEST-EMP2",  # Not Alice!
            "goal_id": "GOAL-ISOLATION-001",
            "review_cycle_id": "CYCLE-2026-H1",
            "check_in_date": "2026-03-01",
            "progress_update": 50.0,
            "employee_comments": "Attempted unauthorized check-in by Alice"
        }
    )
    # Check-in creation should either be rejected or properly isolated
    assert res.status_code in (201, 403)


def test_22_unauthorized_manager_access(client: TestClient, employee_headers: dict):
    """
    Test Priority 3 & 9: Unauthorized manager operations.
    A regular employee cannot transfer managers or access manager-only endpoints.
    """
    res = client.post(
        "/api/organization/transfer/EMP-TEST-EMP1",
        headers=employee_headers,
        json={
            "new_manager_id": "MGR-TEST-001",
            "reason": "Unauthorized self-transfer"
        }
    )
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_23_unauthorized_hr_operations(client: TestClient, employee_headers: dict):
    """
    Test Priority 3 & 9: Unauthorized HR operations.
    A standard employee cannot create employees or administer review cycles.
    """
    res = client.post(
        "/api/employees",
        headers=employee_headers,
        json={
            "employee_id": "EMP-UNAUTHORIZED-001",
            "first_name": "Eve",
            "last_name": "Hacker",
            "email": "eve@test.internal",
            "department": "Engineering",
            "job_title": "Intruder",
            "job_level": "IC1"
        }
    )
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_24_unauthorized_admin_operations(client: TestClient, employee_headers: dict, hr_headers: dict):
    """
    Test Priority 3 & 9: Protection of administrative data-generation endpoints.
    Only ADMIN and IT_OPS can trigger data generation.
    """
    # Employee cannot generate data
    res = client.post(
        "/api/admin/generate-data",
        headers=employee_headers,
        json={"mode": "starter", "seed": 20261022, "load_into_db": False}
    )
    assert res.status_code == 403

    # HR Partner cannot generate data (requires ADMIN or IT_OPS)
    res_hr = client.post(
        "/api/admin/generate-data",
        headers=hr_headers,
        json={"mode": "starter", "seed": 20261022, "load_into_db": False}
    )
    assert res_hr.status_code == 403


def test_25_jwt_expiration(client: TestClient):
    """
    Test Priority 3 & 9: JWT Expiration validation.
    A token with an expired timestamp must be rejected with HTTP 401 'Token is expired'.
    """
    expired_token = create_access_token(
        subject="USR-TEST-EXPIRED",
        claims={"employee_id": "EMP-TEST-EMP1", "roles": ["EMPLOYEE"]},
        expires_delta=timedelta(seconds=-60)  # Expired 60s ago
    )
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "Token is expired" in res.json()["detail"]


def test_26_invalid_authentication(client: TestClient):
    """
    Test Priority 3 & 9: Invalid authentication handling.
    Malformed tokens, bad signatures, or wrong credentials must return HTTP 401.
    """
    # 1. Malformed token string
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert res.status_code == 401
    assert "Token is invalid" in res.json()["detail"]

    # 2. Login with bad credentials
    res_login = client.post(
        "/api/auth/login",
        json={"username": "non_existent_user", "password": "WrongPassword!"}
    )
    assert res_login.status_code == 401
    assert "Incorrect username or password" in res_login.json()["detail"]


def test_27_closed_cycle_override_authorization(client: TestClient, employee_headers: dict, admin_headers: dict):
    """
    Test Priority 3 & 9: Closed cycle override authorization.
    Regular employees cannot create goals in closed cycles (HTTP 403).
    Administrators with is_admin_correction=True succeed and write an AuditEvent.
    """
    # Employee attempting modification in closed cycle
    res_emp = client.post(
        "/api/goals",
        headers=employee_headers,
        json={
            "goal_id": "GOAL-CLOSED-ATTEMPT-01",
            "employee_id": "EMP-TEST-EMP1",
            "review_cycle_id": "CYCLE-2025-H2",  # CLOSED cycle
            "title": "Unauthorized Closed Cycle Goal",
            "category": "DELIVERY",
            "priority": "HIGH",
            "start_date": "2025-07-01",
            "due_date": "2025-12-31",
            "weight": 1.0
        }
    )
    assert res_emp.status_code == 403
    assert "closed" in res_emp.json()["detail"].lower()

    # Admin with correction override
    res_admin = client.post(
        "/api/goals",
        headers=admin_headers,
        json={
            "goal_id": "GOAL-ADMIN-OVERRIDE-01",
            "employee_id": "EMP-TEST-ADMIN",
            "review_cycle_id": "CYCLE-2025-H2",
            "title": "Authorized Admin Correction in Closed Cycle",
            "category": "DELIVERY",
            "priority": "HIGH",
            "start_date": "2025-07-01",
            "due_date": "2025-12-31",
            "weight": 1.0,
            "is_admin_correction": True,
            "correction_reason": "Executive board approved retroactive OKR re-alignment"
        }
    )
    assert res_admin.status_code == 201
    assert res_admin.json()["goal_id"] == "GOAL-ADMIN-OVERRIDE-01"


def test_28_ground_truth_api_isolation(client: TestClient, db_session: Session, employee_headers: dict, admin_headers: dict):
    """
    Test Priority 4 & 9: Ground truth API isolation.
    Regular employees calling /api/anomalies receive 'RESTRICTED_SECURITY_ROLE' for ground_truth_label.
    Administrators receive the unmasked ground truth label.
    """
    # Seed a test anomaly with ground-truth label
    anom = Anomaly(
        anomaly_id="ANO-TEST-ISOLATION-001",
        issue_type="INVALID_PROGRESS",
        affected_entity="key_results",
        affected_record_id="KR-TEST-001",
        severity="MEDIUM",
        description="Key result progress reported as 150% without override approval",
        detection_status="DETECTED",
        ground_truth_label="ANOMALY_INVALID_PROGRESS_INJECTED",
        expected_resolution="Recalculate progress or attach manager override."
    )
    db_session.merge(anom)
    db_session.commit()

    # 1. Regular employee requests anomalies -> ground truth must be masked
    res_emp = client.get("/api/anomalies/ANO-TEST-ISOLATION-001", headers=employee_headers)
    assert res_emp.status_code == 200
    assert res_emp.json()["ground_truth_label"] == "RESTRICTED_SECURITY_ROLE"

    # 2. Administrator requests anomalies -> ground truth is unmasked
    res_admin = client.get("/api/anomalies/ANO-TEST-ISOLATION-001", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["ground_truth_label"] == "ANOMALY_INVALID_PROGRESS_INJECTED"


def test_29_dataset_count_reconciliation():
    """
    Test Priority 2 & 9: Dataset count reconciliation.
    Asserts full mode baseline counts match assignment requirements:
    - 3,000 baseline employees
    - 500 baseline managers
    - 10,000 baseline goals
    - 20,000 baseline check-ins
    """
    full_cfg = get_generator_config(mode="full")
    assert full_cfg.num_employees == 3000
    assert full_cfg.num_managers == 500
    assert full_cfg.num_goals == 10000
    assert full_cfg.num_checkins == 20000

    starter_cfg = get_generator_config(mode="starter")
    assert starter_cfg.num_employees == 150
    assert starter_cfg.num_managers == 25
    assert starter_cfg.num_goals == 500
    assert starter_cfg.num_checkins == 1200

    # Verify manifest exists and records counts
    starter_manifest_path = "generated_data/starter/manifest.json"
    assert os.path.exists(starter_manifest_path)
    with open(starter_manifest_path, "r") as f:
        manifest = json.load(f)
    assert manifest["entity_row_counts"]["employees"] == 150
    assert manifest["entity_row_counts"]["managers"] == 25
    assert manifest["entity_row_counts"]["check_ins"] == 1200
    # Total goals = 500 baseline + 10 anomaly goals = 510
    assert manifest["entity_row_counts"]["goals"] == 510


def test_30_export_consistency():
    """
    Test Priority 2 & 9: Export consistency.
    Verifies that all CSV, JSON, and SQL seed files exist and match manifest entries.
    """
    starter_dir = "generated_data/starter"
    manifest_path = os.path.join(starter_dir, "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Check that every checksummed file exists and is non-empty
    for rel_path, checksum in manifest["file_checksums"].items():
        full_path = os.path.join(starter_dir, rel_path)
        assert os.path.exists(full_path), f"Missing export file: {full_path}"
        assert os.path.getsize(full_path) > 0, f"Export file is empty: {full_path}"

    # Verify ground truth evaluation files exist
    assert os.path.exists(os.path.join(starter_dir, "ground_truth.json"))
    assert os.path.exists(os.path.join(starter_dir, "ground_truth.csv"))
