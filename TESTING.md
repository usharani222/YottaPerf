# YottaPerf — Automated Testing & Verification Evidence

This document catalogs the automated test suite, execution methodology, test invariants, and verification logs for the **YottaPerf** platform.

---

## 1. Test Suite Architecture

The test suite is built on **Pytest 9.2**, **FastAPI TestClient**, **SQLAlchemy 2.0**, and **AnyIO**.

- **Isolation Invariant:** All automated tests execute against an isolated transactional test database runner so that running tests never overwrites or pollutes the production PostgreSQL database.
- **Coverage Scope:** 27 comprehensive integration, security, and invariant tests spanning 7 functional domains:
  1. Employee creation, manager assignment & circular hierarchy DAG rejection
  2. Goals, Key Results, and mathematical progress calculations (increasing & decreasing)
  3. Periodic check-ins, evidence linking, and blocker tracking
  4. 360° feedback eligibility, non-destructive conflict preservation, and review calibration scoring
  5. Closed cycle immutability, cryptographic audit snapshots, and dual-level IDP approvals
  6. Security hardening: RBAC verification, employee data isolation, JWT expiration, login rate limiting, and ground truth API masking
  7. 15-point relational validation engine, dataset count reconciliation, and deterministic seed reproducibility

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

## 3. Verified Execution Log (All 27 Tests Passed)

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /home/gowtham-flint/Desktop/YottaPerf/YottaPerf/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/gowtham-flint/Desktop/YottaPerf/YottaPerf
configfile: pytest.ini
testpaths: backend/tests
plugins: anyio-4.15.1, cov-7.1.0, Faker-40.44.0
collected 27 items                                                             

backend/tests/test_checkins_evidence.py::test_08_and_09_checkin_creation_and_evidence_linking PASSED [  3%]
backend/tests/test_cycles_audit.py::test_14_closed_review_cycle_modification_rejection PASSED [  7%]
backend/tests/test_cycles_audit.py::test_15_audit_history_creation PASSED [ 11%]
backend/tests/test_cycles_audit.py::test_16_development_plan_approval PASSED [ 14%]
backend/tests/test_employees_org.py::test_01_employee_creation PASSED    [ 18%]
backend/tests/test_employees_org.py::test_02_manager_assignment PASSED   [ 22%]
backend/tests/test_employees_org.py::test_03_circular_hierarchy_rejection PASSED [ 25%]
backend/tests/test_feedback_review.py::test_10_reviewer_relationship_validation PASSED [ 29%]
backend/tests/test_feedback_review.py::test_11_conflicting_feedback_handling PASSED [ 33%]
backend/tests/test_feedback_review.py::test_12_review_score_calculation PASSED [ 37%]
backend/tests/test_feedback_review.py::test_13_review_approval_permissions PASSED [ 40%]
backend/tests/test_goals_key_results.py::test_04_goal_creation PASSED    [ 44%]
backend/tests/test_goals_key_results.py::test_05_key_result_progress_calculation PASSED [ 48%]
backend/tests/test_goals_key_results.py::test_06_weighted_goal_progress_calculation PASSED [ 51%]
backend/tests/test_goals_key_results.py::test_07_invalid_progress_rejection PASSED [ 55%]
backend/tests/test_security_rbac_audit.py::test_21_employee_data_isolation PASSED [ 59%]
backend/tests/test_security_rbac_audit.py::test_22_unauthorized_manager_access PASSED [ 62%]
backend/tests/test_security_rbac_audit.py::test_23_unauthorized_hr_operations PASSED [ 66%]
backend/tests/test_security_rbac_audit.py::test_24_unauthorized_admin_operations PASSED [ 70%]
backend/tests/test_security_rbac_audit.py::test_25_jwt_expiration PASSED [ 74%]
backend/tests/test_security_rbac_audit.py::test_26_invalid_authentication PASSED [ 77%]
backend/tests/test_security_rbac_audit.py::test_27_closed_cycle_override_authorization PASSED [ 81%]
backend/tests/test_security_rbac_audit.py::test_28_ground_truth_api_isolation PASSED [ 85%]
backend/tests/test_security_rbac_audit.py::test_29_dataset_count_reconciliation PASSED [ 88%]
backend/tests/test_security_rbac_audit.py::test_30_export_consistency PASSED [ 92%]
backend/tests/test_validation_engine.py::test_17_18_19_validation_engine_integrity_and_anomalies PASSED [ 96%]
backend/tests/test_validation_engine.py::test_20_fixed_seed_reproducibility PASSED [100%]

======================== 27 passed, 2 warnings in 0.91s ========================
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
| **21** | `test_21_employee_data_isolation` | Verifies employee isolation; non-managerial employees cannot inject check-ins into colleagues' goals. |
| **22** | `test_22_unauthorized_manager_access` | Rejects manager transfer operations attempted by regular employees with HTTP 403. |
| **23** | `test_23_unauthorized_hr_operations` | Enforces HR role requirement for creating new employees and administering review cycles. |
| **24** | `test_24_unauthorized_admin_operations` | Protects administrative synthetic data generation endpoints; rejects employee/HR attempts with HTTP 403. |
| **25** | `test_25_jwt_expiration` | Validates expired JWT bearer tokens are rejected with HTTP 401 (`Token is expired`). |
| **26** | `test_26_invalid_authentication` | Validates malformed token strings and invalid user credentials return HTTP 401. |
| **27** | `test_27_closed_cycle_override_authorization` | Prohibits employee modifications to closed cycles; permits authorized administrator overrides with audit logging. |
| **28** | `test_28_ground_truth_api_isolation` | Verifies anomaly ground truth labels are strictly masked as `RESTRICTED_SECURITY_ROLE` for non-admin users. |
| **29** | `test_29_dataset_count_reconciliation` | Reconciles generator configurations against authoritative assignment requirements (3k employees, 500 managers, 10k baseline goals, 20k check-ins). |
| **30** | `test_30_export_consistency` | Verifies manifest checksums and guarantees all CSV, JSON, and SQL exports are present and non-empty. |
