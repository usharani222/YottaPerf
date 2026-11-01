# Anomaly Catalog: YottaPerf Platform

This catalog defines the taxonomy of deliberate synthetic anomalies, detection signatures, severity criteria, and expected remediation strategies implemented in YottaPerf.

---

## 1. Required Anomalies Taxonomy

### Anomaly 1: GOAL OWNER MISMATCH (`GOAL_OWNER_MISMATCH`)
- **Severity**: HIGH
- **Affected Entity**: `goals`
- **Description**: A goal record is assigned to an employee who does not belong to the target organizational unit, or whose ID mismatch indicates unauthorized reassignment or erroneous data migration.
- **Detection Query / Heuristic**:
  - `goals.employee_id != originating_author` where the goal creation payload and owner diverge without delegation approval, or a goal is linked to an employee whose hiring date is post-goal creation.
- **Ground Truth Label**: `ANOMALY_GOAL_OWNER_MISMATCH`
- **Expected Resolution**: Reassign goal to authentic owner or quarantine the record for managerial validation.

### Anomaly 2: INVALID PROGRESS (`INVALID_PROGRESS`)
- **Severity**: CRITICAL
- **Affected Entity**: `key_results` / `goals`
- **Description**: Progress percentage calculation deviates from ground-truth formula (e.g., progress reported as 250% when current value barely matches baseline, or negative percentages without valid rationale).
- **Detection Query / Heuristic**:
  - Compare `progress_percentage` against recomputed formula value $\left|\text{reported} - \text{computed}\right| > 0.01$.
- **Ground Truth Label**: `ANOMALY_INVALID_PROGRESS`
- **Expected Resolution**: Trigger automatic recalculation from baseline, target, and current observations.

### Anomaly 3: INVALID REVIEWER (`INVALID_REVIEWER`)
- **Severity**: MEDIUM
- **Affected Entity**: `feedbacks`
- **Description**: A peer or 360-degree feedback entry was authored by an employee with no organizational, project, or reporting relationship to the subject employee.
- **Detection Query / Heuristic**:
  - `feedbacks.reviewer_employee_id` has no shared manager, different department, no cross-functional permission in `review_permissions`, and is not the subject's direct manager.
- **Ground Truth Label**: `ANOMALY_INVALID_REVIEWER`
- **Expected Resolution**: Invalidate or discard unverified feedback before review score computation.

### Anomaly 4: CLOSED CYCLE MODIFICATION (`CLOSED_CYCLE_MODIFICATION`)
- **Severity**: CRITICAL
- **Affected Entity**: `goals` / `reviews` / `review_cycles`
- **Description**: An appraisal or goal record was modified or created with a timestamp after the review cycle stage was set to `CLOSED` or `ARCHIVED`, without an accompanying authorized `AuditEvent`.
- **Detection Query / Heuristic**:
  - Target `review_cycles.stage IN ('CLOSED', 'ARCHIVED')` AND record updated after cycle `end_date` AND missing valid `AuditEvent` with `operation_type = 'CORRECTION'`.
- **Ground Truth Label**: `ANOMALY_CLOSED_CYCLE_MODIFICATION`
- **Expected Resolution**: Roll back modifications to the last approved snapshot and audit the unauthorized actor.

### Anomaly 5: UNTRACEABLE FEEDBACK (`UNTRACEABLE_FEEDBACK`)
- **Severity**: MEDIUM
- **Affected Entity**: `feedbacks`
- **Description**: A high-impact or divergent feedback rating (>4.5 or <2.0) exists without required descriptive comments, author identity, or verifiable evidence attachments.
- **Detection Query / Heuristic**:
  - `feedbacks.rating NOT BETWEEN 2.5 AND 3.5` AND (`comments IS NULL` OR `LENGTH(comments) < 15`) AND missing linked entries in `feedback_evidence`.
- **Ground Truth Label**: `ANOMALY_UNTRACEABLE_FEEDBACK`
- **Expected Resolution**: Flag feedback as unverified; prompt reviewer for evidence or exclude from calibration.

---

## 2. Extended Anomalies

### Anomaly 6: CIRCULAR HIERARCHY (`CIRCULAR_HIERARCHY`)
- **Severity**: CRITICAL
- **Affected Entity**: `employees`
- **Description**: A reporting cycle is present in the managerial hierarchy (e.g., A -> B -> C -> A).
- **Ground Truth Label**: `ANOMALY_CIRCULAR_HIERARCHY`
- **Expected Resolution**: Break cycle by reassigning root manager.

---

## 3. Anomaly Lifecycle & Ground Truth Isolation

- Deliberate anomalies are generated in dedicated batches or during synthetic injection passes.
- Ground truth metadata (`ground_truth.csv` and `ground_truth.json`) records the exact record ID, issue type, expected classification, and explanation.
- **Security Rule**: Ground truth files are kept strictly isolated from normal application runtime APIs and feature extractors.
