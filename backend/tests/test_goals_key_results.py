import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.services.goal_service import (
    GoalService, calculate_kr_progress, InvalidProgressException
)
from backend.app.models.goal import Goal


def test_04_goal_creation(client: TestClient, admin_headers: dict):
    """TEST 4: Goal creation."""
    payload = {
        "goal_id": "GOAL-TEST-001",
        "employee_id": "EMP-000991",
        "review_cycle_id": "CYCLE-2026-H1",
        "title": "Build Resilient Distributed Caching Layer",
        "description": "Improve API latency via distributed Redis caching",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "start_date": "2026-01-01",
        "due_date": "2026-06-30",
        "weight": 1.0
    }
    response = client.post("/api/goals", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["goal_id"] == "GOAL-TEST-001"
    assert data["status"] == "DRAFT"
    assert data["calculated_progress"] == 0.0


def test_05_key_result_progress_calculation():
    """TEST 5: Key Result progress formula calculation for increasing and decreasing metrics."""
    # Case A: Increasing metric (baseline 10.0, target 50.0, current 30.0) -> (30-10)/(50-10) = 50.0%
    prog_inc = calculate_kr_progress("INCREASING", 10.0, 50.0, 30.0)
    assert prog_inc == 50.0

    # Case B: Decreasing metric (latency from 300ms down to 100ms, current 150ms)
    # (300 - 150) / (300 - 100) = 150 / 200 = 75.0%
    prog_dec = calculate_kr_progress("DECREASING", 300.0, 100.0, 150.0)
    assert prog_dec == 75.0

    # Boundary: Zero denominator handled defensively
    prog_zero = calculate_kr_progress("INCREASING", 100.0, 100.0, 100.0)
    assert prog_zero == 100.0


def test_06_weighted_goal_progress_calculation(client: TestClient, admin_headers: dict):
    """TEST 6: Weighted goal progress calculation from multiple Key Results."""
    # Add KR 1: weight 1.0, baseline 0, target 100, current 50 -> 50%
    kr1_payload = {
        "key_result_id": "KR-GOAL-TEST-001-01",
        "metric_name": "Cache Hit Ratio",
        "baseline_value": 0.0,
        "target_value": 100.0,
        "current_value": 50.0,
        "unit": "PERCENT",
        "metric_direction": "INCREASING",
        "weight": 1.0
    }
    res1 = client.post("/api/goals/GOAL-TEST-001/key-results", json=kr1_payload, headers=admin_headers)
    assert res1.status_code == 201, res1.text

    # Add KR 2: weight 3.0, baseline 0, target 100, current 100 -> 100%
    kr2_payload = {
        "key_result_id": "KR-GOAL-TEST-001-02",
        "metric_name": "Cluster Node Redundancy",
        "baseline_value": 0.0,
        "target_value": 100.0,
        "current_value": 100.0,
        "unit": "PERCENT",
        "metric_direction": "INCREASING",
        "weight": 3.0
    }
    res2 = client.post("/api/goals/GOAL-TEST-001/key-results", json=kr2_payload, headers=admin_headers)
    assert res2.status_code == 201, res2.text

    # Reconciled progress should be weighted:
    # ((50.0 * 1.0) + (100.0 * 3.0)) / (1.0 + 3.0) = (50 + 300) / 4.0 = 87.5%
    goal_res = client.get("/api/goals/GOAL-TEST-001", headers=admin_headers)
    assert goal_res.status_code == 200
    goal_data = goal_res.json()
    assert goal_data["calculated_progress"] == 87.5
    assert goal_data["status"] == "ACTIVE"


def test_07_invalid_progress_rejection(client: TestClient, admin_headers: dict):
    """TEST 7: Invalid progress rejection when scale exceeds bounds (> 200%)."""
    # Current value 350 on 0-100 scale = 350% -> triggers InvalidProgressException
    kr_invalid_payload = {
        "key_result_id": "KR-GOAL-TEST-001-03",
        "metric_name": "Exceeded Metric",
        "baseline_value": 0.0,
        "target_value": 100.0,
        "current_value": 350.0,
        "unit": "PERCENT",
        "metric_direction": "INCREASING",
        "weight": 1.0
    }
    response = client.post("/api/goals/GOAL-TEST-001/key-results", json=kr_invalid_payload, headers=admin_headers)
    assert response.status_code == 422
    assert "exceeds" in response.json()["detail"].lower()
