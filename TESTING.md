# YottaPerf — Automated Testing & Verification Evidence

This document catalogs the automated test suite, execution methodology, test invariants, and verification logs for the **YottaPerf** platform.

---

## 1. Test Suite Architecture

The test suite is built on **Pytest 9.2**, **FastAPI TestClient**, **SQLAlchemy 2.0**, and **AnyIO**.

- **Isolation Invariant:** All automated tests execute against an isolated transactional test database runner so that running tests never overwrites or pollutes the production PostgreSQL database.
- **Coverage Scope:** 17 comprehensive integration and invariant tests spanning 6 functional domains:
  1. Employee creation, manager assignment & circular hierarchy DAG rejection
  2. Goals, Key Results, and mathematical progress calculations (increasing & decreasing)
  3. Periodic check-ins, evidence linking, and blocker tracking
  4. 360° feedback eligibility, non-destructive conflict preservation, and review calibration scoring
  5. Closed cycle immutability, cryptographic audit snapshots, and dual-level IDP approvals
  6. 15-point relational validation engine and deterministic seed reproducibility

---

## 2. Test Execution Command

Run the complete test suite directly from the project root:

```bash
# Using Python virtual environment
venv/bin/pytest -v

# Or inside the isolated Docker container
docker compose exec backend pytest backend/tests/ -v
```

---

## 3. Verified Execution Log (All 17 Tests Passed)

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/gowtham-flint/Desktop/YottaPerf/YottaPerf
configfile: pytest.ini
testpaths: backend/tests
plugins: anyio-4.15.1, cov-7.1.0, Faker-40.44.0
collected 17 items                                                             

backend/tests/test_checkins_evidence.py::test_08_and_09_checkin_creation_and_evidence_linking PASSED [  5%]
backend/tests/test_cycles_audit.py::test_14_closed_review_cycle_modification_rejection PASSED [ 11%]
backend/tests/test_cycles_audit.py::test_15_audit_history_creation PASSED [ 17%]
backend/tests/test_cycles_audit.py::test_16_development_plan_approval PASSED [ 23%]
backend/tests/test_employees_org.py::test_01_employee_creation PASSED    [ 29%]
backend/tests/test_employees_org.py::test_02_manager_assignment PASSED   [ 35%]
backend/tests/test_employees_org.py::test_03_circular_hierarchy_rejection PASSED [ 41%]
backend/tests/test_feedback_review.py::test_10_reviewer_relationship_validation PASSED [ 47%]
backend/tests/test_feedback_review.py::test_11_conflicting_feedback_handling PASSED [ 52%]
backend/tests/test_feedback_review.py::test_12_review_score_calculation PASSED [ 58%]
backend/tests/test_feedback_review.py::test_13_review_approval_permissions PASSED [ 64%]
backend/tests/test_goals_key_results.py::test_04_goal_creation PASSED    [ 70%]
backend/tests/test_goals_key_results.py::test_05_key_result_progress_calculation PASSED [ 76%]
backend/tests/test_goals_key_results.py::test_06_weighted_goal_progress_calculation PASSED [ 82%]
backend/tests/test_goals_key_results.py::test_07_invalid_progress_rejection PASSED [ 88%]
backend/tests/test_validation_engine.py::test_17_18_19_validation_engine_integrity_and_anomalies PASSED [ 94%]
backend/tests/test_validation_engine.py::test_20_fixed_seed_reproducibility PASSED [100%]

======================== 17 passed in 0.75s ========================
```

---

## 4. Test Catalog & Functional Assertions

| Test ID | Test Function | Description & Invariant Tested |
|---|---|---|
| **01** | `test_01_employee_creation` | Verifies employee profile creation, email uniqueness, department assignment, and zero-padded `EMP-NNNNNN` ID format. |
| **02** | `test_02_manager_assignment` | Verifies active manager assignment and historical transition logging in `employee_manager_histories`. |
| **03** | `test_03_circular_hierarchy_rejection` | Attempts to create circular reporting loops (A &rarr; B &rarr; C &rarr; A); asserts DFS traversal aborts mutation with HTTP 400. |
| **04** | `test_04_goal_creation` | Verifies goal creation with active review cycle linkage, priority constraints, and parent-child ownership. |
| **05** | `test_05_key_result_progress_calculation` | Validates increasing metric and decreasing metric formulas with edge cases ($curr < base$, $curr > tgt$). |
| **06** | `test_06_weighted_goal_progress_calculation` | Reconciles goal overall progress against sum of child Key Result weights ($\sum w_i = 100\%$). |
| **07** | `test_07_invalid_progress_rejection` | Injects out-of-bounds progress values (>100% without approval); asserts strict rejection. |
| **08 & 09** | `test_08_and_09_checkin_creation_and_evidence_linking` | Creates periodic check-ins and binds verifiable evidence artifacts (`CODE_PR`, `DASHBOARD`, `DOCUMENT`). |
| **10** | `test_10_reviewer_relationship_validation` | Validates 360° feedback requests against organizational reporting and collaboration graphs. |
| **11** | `test_11_conflicting_feedback_handling` | Submits divergent evaluations across multiple reviewers; verifies conflicting scores are preserved non-destructively. |
| **12** | `test_12_review_score_calculation` | Evaluates composite formula: $(0.50 \times \text{Goals}) + (0.30 \times \text{Competencies}) + (0.20 \times \text{Feedback})$. |
| **13** | `test_13_review_approval_permissions` | Enforces stage transitions and asserts employees cannot self-approve their own performance review. |
| **14** | `test_14_closed_review_cycle_modification_rejection` | Rejects non-administrative updates targeting a cycle in `CLOSED` state with HTTP 403. |
| **15** | `test_15_audit_history_creation` | Validates that administrative overrides capture serialized previous state and new state diffs in `audit_events`. |
| **16** | `test_16_development_plan_approval` | Verifies dual-approval workflow (Manager + HR) for employee Individual Development Plans (IDPs). |
| **17-19** | `test_17_18_19_validation_engine_integrity_and_anomalies` | Executes 15-point validation engine against dataset; verifies 100% anomaly detection precision/recall. |
| **20** | `test_20_fixed_seed_reproducibility` | Generates two independent dataset runs with seed `20261022`; verifies bit-for-bit SHA-256 match. |
