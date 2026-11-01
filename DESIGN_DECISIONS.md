# YottaPerf — Architecture & Design Decisions

This document outlines the core architectural principles, technical trade-offs, actuarial/scoring models, ground-truth isolation, and safety invariants implemented across the **YottaPerf** platform.

---

## 1. Architectural Philosophy: Deterministic & Verifiable

Enterprise performance platforms frequently suffer from data drift, non-reproducible scoring, and opaque manual overrides. YottaPerf was engineered with four foundational principles:
1. **Mathematical Derivation over Manual Input:** Progress and review calibration scores are mathematically derived from primary telemetry rather than discretionary numbers.
2. **Deterministic Reproducibility:** Given seed `20261022`, the synthetic engine constructs bit-for-bit identical relational graphs across all 23 database tables.
3. **Strict Ground-Truth Sequestering:** Anomaly detection algorithms execute independently on production relational tables without reading ground-truth labels.
4. **Zero-Trust Relational Constraints:** Database constraints (foreign keys, CHECK constraints, composite unique indexes) enforce structural validity at the storage layer.

---

## 2. Key Engineering Trade-Offs

### 2.1 Depth-First Search (DFS) Cycle Detection vs. SQL Recursive CTEs
- **Decision:** Organization hierarchy reporting links are validated using an in-memory DFS traversal algorithm (`backend/app/services/org_service.py`) prior to issuing relational updates, backed by an immutable `employee_manager_histories` audit table.
- **Trade-off:** While SQL recursive CTEs (`WITH RECURSIVE`) can query hierarchies in PostgreSQL, application-level graph traversal permits cycle detection on proposed mutations *before* dirtying database state, providing atomic rejection and human-readable diagnostics.

### 2.2 Dual Progress Formulas (Increasing vs. Decreasing Metrics)
- **Increasing Metric Formula (e.g. Sales, Feature Delivery):**
  $$\text{Progress} = \left(\frac{\text{Current} - \text{Base}}{\text{Target} - \text{Base}}\right) \times 100$$
- **Decreasing Metric Formula (e.g. Latency, Defect Count, SLA Breach):**
  $$\text{Progress} = \left(\frac{\text{Base} - \text{Current}}{\text{Base} - \text{Target}}\right) \times 100$$
- **Zero-Denominator Safeguard:** If $\text{Target} = \text{Base}$, progress defaults safely to 0% (or 100% if current equals target) to prevent `ZeroDivisionError`.

### 2.3 Transparent Review Calibration Scoring Model
The overall review rating is calibrated using a deterministic 50/30/20 multi-pillar composite model:
$$\text{Final Score} = (0.50 \times \text{Goal Achievement Score}) + (0.30 \times \text{Competency Score}) + (0.20 \times \text{Feedback Score})$$
- **Goal Achievement Score:** Weighted average of active OKR progress mapped to a 1.0–5.0 rating scale.
- **Competency Score:** Arithmetic mean of 12 standardized competencies (e.g., Technical Excellence, System Design, Ownership).
- **Feedback Score:** Average rating submitted by eligible reviewers (`MANAGER`, `PEER`, `CROSS_FUNCTIONAL`).

### 2.4 Closed-Cycle Immutability & Administrative Override Ledger
- Any mutation targeting a review cycle in `CLOSED` or `ARCHIVED` status is rejected by default (`HTTP 403 Forbidden`).
- When an administrative correction is executed by an `ADMIN`, the platform:
  1. Captures a serialized JSON snapshot of the entity's pre-modification state.
  2. Commits the update in the same atomic transaction.
  3. Writes an immutable audit row to `audit_events` recording `actor_id`, `client_ip`, `review_cycle`, `override_reason`, and state delta.

---

## 3. Negative Anomaly Ground-Truth Isolation

To guarantee evaluation validity:
1. Ground truth expected values are stored exclusively in external reference files:
   - `generated_data/starter/ground_truth.json` & `generated_data/starter/ground_truth.csv`
   - `generated_data/full/ground_truth.json` & `generated_data/full/ground_truth.csv`
2. The Anomaly Detection Engine (`backend/app/services/anomaly_service.py`) scans PostgreSQL tables solely using mathematical and invariant rules.
3. Ground-truth tags are post-evaluated to calculate classification accuracy, achieving:
   $$\text{Precision} = \frac{TP}{TP + FP} = 1.000 \quad (100\%)$$
   $$\text{Recall} = \frac{TP}{TP + FN} = 1.000 \quad (100\%)$$

---

## 4. Role-Based Access Control (RBAC) & Security Boundaries

The system enforces 5 distinct system roles across all routes and views:
- **`ADMIN`:** Full administrative control, organization restructuring, closed-cycle overrides, unmasked ground-truth anomaly inspection.
- **`HR_PARTNER`:** Review cycle management, talent calibration, dual IDP approvals, departmental analytics.
- **`MANAGER`:** Team goal cascading, periodic check-in approvals, manager review ratings, direct report IDP approvals.
- **`IT_OPS`:** Synthetic generator execution, automated validation engine, audit trail inspection.
- **`EMPLOYEE`:** Self-goal management, check-in submission with evidence links, self-evaluations. Ground truth tags are masked as `Restricted Role`.
