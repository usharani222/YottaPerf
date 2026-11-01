# Data Dictionary: YottaPerf Platform

This document defines the schema, field types, constraints, deterministic ID formats, and semantics for all entities in the YottaPerf platform.

---

## 1. Core Entities

### 1.1 `employees`
Stores employee profiles, job titles, department mappings, and reporting hierarchy.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `employee_id` | VARCHAR(32) | NO | PRIMARY KEY | Deterministic ID format: `EMP-000001` |
| `first_name` | VARCHAR(100) | NO | | First name |
| `last_name` | VARCHAR(100) | NO | | Last name |
| `email` | VARCHAR(255) | NO | UNIQUE | Corporate email address |
| `department` | VARCHAR(100) | NO | | Department (Engineering, Product, Sales, etc.) |
| `job_title` | VARCHAR(100) | NO | | Official designation / title |
| `job_level` | VARCHAR(20) | NO | | Seniority level (IC1 - IC6, M1 - M4, Exec) |
| `manager_id` | VARCHAR(32) | YES | FK -> `employees.employee_id` | Direct manager (NULL for CEO) |
| `is_active` | BOOLEAN | NO | DEFAULT TRUE | Active employment status flag |
| `hire_date` | DATE | NO | | Date of joining organization |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Audit creation timestamp |
| `updated_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Audit modification timestamp |

### 1.2 `managers`
Stores manager-specific metadata and span of control.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `manager_id` | VARCHAR(32) | NO | PRIMARY KEY | Deterministic ID: `MGR-000001` |
| `employee_id` | VARCHAR(32) | NO | UNIQUE, FK -> `employees.employee_id` | Employee representing the manager |
| `management_level` | VARCHAR(50) | NO | | Team Lead, Director, VP, Executive |
| `budget_authority` | NUMERIC(14,2)| NO | DEFAULT 0.00 | Authorized operational budget |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### 1.3 `review_cycles`
Defines time-boxed performance appraisal periods.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `cycle_id` | VARCHAR(32) | NO | PRIMARY KEY | Deterministic ID format: `CYCLE-2026-H1` |
| `cycle_name` | VARCHAR(100) | NO | | Display title (e.g. 2026 H1 Performance Cycle) |
| `start_date` | DATE | NO | | Cycle start date |
| `end_date` | DATE | NO | CHECK (`end_date` > `start_date`)| Cycle end date |
| `submission_deadline`| DATE | NO | | Employee self-review deadline |
| `stage` | VARCHAR(50) | NO | DEFAULT 'UPCOMING' | `UPCOMING`, `OPEN`, `EVALUATION`, `CLOSED`, `ARCHIVED` |
| `goal_weight` | NUMERIC(5,2)| NO | DEFAULT 50.00 | Goal contribution percentage to review score |
| `competency_weight`| NUMERIC(5,2)| NO | DEFAULT 30.00 | Competency contribution percentage |
| `feedback_weight`| NUMERIC(5,2)| NO | DEFAULT 20.00 | Feedback contribution percentage |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Modification timestamp |

### 1.4 `goals`
Represents an individual or team strategic objective.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `goal_id` | VARCHAR(64) | NO | PRIMARY KEY | Deterministic ID: `GOAL-EMP-000001-001` |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.employee_id` | Goal owner |
| `review_cycle_id`| VARCHAR(32) | NO | FK -> `review_cycles.cycle_id` | Target review cycle |
| `title` | VARCHAR(255) | NO | | Summary of the goal |
| `description` | TEXT | YES | | Detailed objective specification |
| `category` | VARCHAR(50) | NO | | `TECHNICAL`, `LEADERSHIP`, `DELIVERY`, `CUSTOMER`, `LEARNING` |
| `priority` | VARCHAR(20) | NO | DEFAULT 'MEDIUM' | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `start_date` | DATE | NO | | Goal effective start date |
| `due_date` | DATE | NO | CHECK (`due_date` >= `start_date`) | Goal deadline |
| `weight` | NUMERIC(5,2)| NO | DEFAULT 1.0, CHECK (`weight` > 0)| Relative weight among employee goals |
| `calculated_progress`| NUMERIC(5,2)| NO | DEFAULT 0.00 | Weighted sum of child Key Result progress |
| `status` | VARCHAR(50) | NO | DEFAULT 'DRAFT' | `DRAFT`, `SUBMITTED`, `ACTIVE`, `COMPLETED`, `CANCELLED` |
| `created_by` | VARCHAR(32) | NO | FK -> `employees.employee_id` | Author |
| `approved_by` | VARCHAR(32) | YES | FK -> `employees.employee_id` | Manager approver |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |
| `updated_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

### 1.5 `key_results`
Quantifiable outcomes underpinning goals.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `key_result_id` | VARCHAR(64) | NO | PRIMARY KEY | Format: `KR-GOAL-EMP-000001-001-01` |
| `goal_id` | VARCHAR(64) | NO | FK -> `goals.goal_id` CASCADE | Parent goal |
| `metric_name` | VARCHAR(200) | NO | | Name of measurable indicator |
| `metric_direction`| VARCHAR(20) | NO | DEFAULT 'INCREASING' | `INCREASING` or `DECREASING` |
| `baseline_value` | NUMERIC(12,2)| NO | | Initial baseline measurement |
| `target_value` | NUMERIC(12,2)| NO | | Expected target measurement |
| `current_value` | NUMERIC(12,2)| NO | | Current measured value |
| `unit` | VARCHAR(50) | NO | | `PERCENT`, `COUNT`, `USD`, `DAYS`, `HOURS` |
| `weight` | NUMERIC(5,2)| NO | DEFAULT 1.0, CHECK (`weight` > 0)| Relative weight in the goal |
| `progress_percentage`| NUMERIC(6,2)| NO| DEFAULT 0.00 | Derived formula percentage |
| `status` | VARCHAR(50) | NO | DEFAULT 'ON_TRACK' | `ON_TRACK`, `AT_RISK`, `BEHIND`, `ACHIEVED` |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |
| `updated_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

### 1.6 `check_ins`
Periodic milestone progress updates.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `check_in_id` | VARCHAR(32) | NO | PRIMARY KEY | Format: `CHK-000001` |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.employee_id` | Submitting employee |
| `goal_id` | VARCHAR(64) | NO | FK -> `goals.goal_id` | Target goal |
| `review_cycle_id`| VARCHAR(32) | NO | FK -> `review_cycles.cycle_id` | Review cycle |
| `check_in_date` | DATE | NO | | Submission date |
| `progress_update`| NUMERIC(5,2)| NO | | Reported progress update |
| `employee_comments`| TEXT | NO | | Employee commentary |
| `manager_comments`| TEXT | YES | | Manager feedback commentary |
| `blockers` | TEXT | YES | | Impediments identified |
| `next_steps` | TEXT | YES | | Forward commitments |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

### 1.7 `competencies`
Standard organizational capability definitions.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `competency_id` | VARCHAR(32) | NO | PRIMARY KEY | E.g., `COMP-TECH-01`, `COMP-COMM-01` |
| `category` | VARCHAR(100) | NO | | Technical Skills, Communication, etc. |
| `name` | VARCHAR(150) | NO | | Name of capability |
| `description` | TEXT | NO | | Behavioral expectations and rubric |
| `is_active` | BOOLEAN | NO | DEFAULT TRUE | Active flag |

### 1.8 `feedbacks`
360-degree feedback entries (Self, Manager, Peer).

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `feedback_id` | VARCHAR(32) | NO | PRIMARY KEY | Format: `FB-000001` |
| `subject_employee_id`| VARCHAR(32)| NO | FK -> `employees.employee_id` | Feedback recipient |
| `reviewer_employee_id`| VARCHAR(32)| NO | FK -> `employees.employee_id`| Author |
| `review_cycle_id`| VARCHAR(32) | NO | FK -> `review_cycles.cycle_id` | Appraisal cycle |
| `feedback_type` | VARCHAR(30) | NO | | `SELF`, `MANAGER`, `PEER` |
| `competency_id` | VARCHAR(32) | NO | FK -> `competencies.competency_id` | Evaluated capability |
| `rating` | NUMERIC(3,2)| NO | CHECK (`rating` >= 1.0 AND `rating` <= 5.0) | Rating 1.00 to 5.00 |
| `comments` | TEXT | NO | | Qualitative evidence / notes |
| `submission_date`| DATE | NO | | Submission date |
| `status` | VARCHAR(30) | NO | DEFAULT 'SUBMITTED' | `DRAFT`, `SUBMITTED`, `REVISED` |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

### 1.9 `reviews`
Formal performance appraisal reviews.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `review_id` | VARCHAR(32) | NO | PRIMARY KEY | Format: `REV-2026-000001` |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.employee_id` | Review subject |
| `review_cycle_id`| VARCHAR(32) | NO | FK -> `review_cycles.cycle_id` | Appraisal cycle |
| `goal_score` | NUMERIC(5,2)| NO | DEFAULT 0.00 | Computed goal achievement score |
| `competency_score`| NUMERIC(5,2)| NO | DEFAULT 0.00 | Computed competency score |
| `feedback_score`| NUMERIC(5,2)| NO | DEFAULT 0.00 | Computed feedback score |
| `final_score` | NUMERIC(5,2)| NO | DEFAULT 0.00 | Weighted total performance score |
| `rating_category`| VARCHAR(50) | NO | DEFAULT 'MEETS_EXPECTATIONS'| `NEEDS_IMPROVEMENT`, `MEETS`, `EXCEEDS`, `OUTSTANDING` |
| `stage` | VARCHAR(50) | NO | DEFAULT 'DRAFT' | Lifecycle stage |
| `self_submitted_at`| TIMESTAMPTZ| YES | | Self-appraisal completion timestamp |
| `manager_approved_at`| TIMESTAMPTZ| YES| | Manager approval timestamp |
| `hr_approved_at` | TIMESTAMPTZ | YES | | HR calibration timestamp |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |
| `updated_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

### 1.10 `development_plans`
Targeted career growth and capability gap plans.

| Column | Type | Nullable | Constraints / Default | Description |
|---|---|---|---|---|
| `plan_id` | VARCHAR(32) | NO | PRIMARY KEY | Format: `DP-000001` |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.employee_id` | Plan owner |
| `review_id` | VARCHAR(32) | YES | FK -> `reviews.review_id` | Originating review |
| `competency_id` | VARCHAR(32) | NO | FK -> `competencies.competency_id` | Target capability |
| `current_level` | VARCHAR(50) | NO | | Starting baseline proficiency |
| `target_level` | VARCHAR(50) | NO | | Expected proficiency goal |
| `recommended_action`| TEXT | NO | | Action plan and milestones |
| `learning_resources`| TEXT | YES | | Recommended courses/books |
| `start_date` | DATE | NO | | Start date |
| `target_completion_date`| DATE | NO | CHECK (`target_completion_date` >= `start_date`)| Target completion date |
| `status` | VARCHAR(30) | NO | DEFAULT 'IN_PROGRESS' | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| `approval_status`| VARCHAR(30) | NO | DEFAULT 'PENDING' | `PENDING`, `APPROVED`, `REJECTED` |
| `created_at` | TIMESTAMPTZ | NO | DEFAULT CURRENT_TIMESTAMP | Timestamp |

---

## 2. Supporting & Audit Entities

### 2.1 `employee_manager_histories`
Records reporting structure evolution over time.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `history_id` | VARCHAR(32) | PRIMARY KEY | Deterministic ID |
| `employee_id` | VARCHAR(32) | FK -> `employees.employee_id` | Employee transferred |
| `manager_id` | VARCHAR(32) | FK -> `employees.employee_id` | Manager assigned |
| `effective_start_date`| DATE | NOT NULL | Assignment start |
| `effective_end_date` | DATE | YES | Assignment end (NULL for active) |
| `transfer_reason` | VARCHAR(255) | | Reason for transfer |

### 2.2 `evidences`
Verifiable documentation supporting goals and check-ins.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `evidence_id` | VARCHAR(32) | PRIMARY KEY | Format: `EVD-000001` |
| `check_in_id` | VARCHAR(32) | YES, FK -> `check_ins.check_in_id` | Associated check-in |
| `evidence_type` | VARCHAR(50) | NOT NULL | `CODE_PR`, `METRIC_DASHBOARD`, `CUSTOMER_EMAIL`, `CERTIFICATION`, `DOCUMENT` |
| `reference_url` | VARCHAR(500)| NOT NULL | URI or artifact storage path |
| `description` | TEXT | NOT NULL | Verification context |
| `uploaded_by` | VARCHAR(32) | FK -> `employees.employee_id` | Uploader ID |
| `uploaded_date` | DATE | NOT NULL | Date attached |
| `verification_status`| VARCHAR(30)| DEFAULT 'VERIFIED' | `VERIFIED`, `PENDING_REVIEW`, `REJECTED` |

### 2.3 `goal_histories`
Immutable version snapshots of goals.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `history_id` | VARCHAR(32) | PRIMARY KEY | Snapshot ID |
| `goal_id` | VARCHAR(64) | FK -> `goals.goal_id` | Target goal |
| `version_number` | INTEGER | NOT NULL | Sequential version |
| `title` | VARCHAR(255) | NOT NULL | Snapshot title |
| `status` | VARCHAR(50) | NOT NULL | Snapshot status |
| `calculated_progress`| NUMERIC(5,2)| NOT NULL | Snapshot progress |
| `changed_by` | VARCHAR(32) | FK -> `employees.employee_id` | Modifying actor |
| `change_reason` | VARCHAR(255) | NOT NULL | Audit justification |
| `changed_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |

### 2.4 `audit_events`
Enterprise immutable security and business event ledger.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `event_id` | VARCHAR(32) | PRIMARY KEY | Format: `AUD-000001` |
| `actor_id` | VARCHAR(32) | FK -> `employees.employee_id` | Acting user |
| `entity_name` | VARCHAR(50) | NOT NULL | `GOAL`, `REVIEW`, `CYCLE`, `MANAGER_TRANSFER`, etc. |
| `entity_id` | VARCHAR(64) | NOT NULL | Target entity record ID |
| `operation_type` | VARCHAR(20) | NOT NULL | `CREATE`, `UPDATE`, `DELETE`, `TRANSITION`, `CORRECTION` |
| `old_values` | JSONB | YES | State before change |
| `new_values` | JSONB | YES | State after change |
| `review_cycle_id`| VARCHAR(32) | YES | Associated review cycle |
| `reason` | VARCHAR(255) | YES | Administrative reason |
| `timestamp` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Tamper-proof timestamp |

### 2.5 `anomalies`
Exception registry for detected system inconsistencies and injected scenarios.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `anomaly_id` | VARCHAR(32) | PRIMARY KEY | Format: `ANO-000001` |
| `issue_type` | VARCHAR(50) | NOT NULL | `GOAL_OWNER_MISMATCH`, `INVALID_PROGRESS`, `INVALID_REVIEWER`, `CLOSED_CYCLE_MODIFICATION`, `UNTRACEABLE_FEEDBACK` |
| `affected_entity`| VARCHAR(50) | NOT NULL | Entity table name |
| `affected_record_id`| VARCHAR(64)| NOT NULL | Record ID exhibiting anomaly |
| `severity` | VARCHAR(20) | NOT NULL | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `description` | TEXT | NOT NULL | Diagnostic explanation |
| `detection_status`| VARCHAR(30)| DEFAULT 'DETECTED' | `DETECTED`, `INVESTIGATING`, `RESOLVED`, `FALSE_POSITIVE` |
| `ground_truth_label`| VARCHAR(50)| NOT NULL | Expected anomaly classification |
| `expected_resolution`| TEXT | NOT NULL | Recommended remediation |
| `detection_timestamp`| TIMESTAMPTZ| DEFAULT CURRENT_TIMESTAMP| Time detected |

### 2.6 `roles`
Defines RBAC security roles across the platform.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `role_id` | VARCHAR(32) | PRIMARY KEY | Format: `ROLE-ADMIN`, `ROLE-MGR`, etc. |
| `name` | VARCHAR(50) | UNIQUE, NOT NULL | `ADMIN`, `HR_PARTNER`, `MANAGER`, `EMPLOYEE`, `IT_OPS` |
| `description` | TEXT | | Human-readable role authority description |
| `created_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### 2.7 `employee_roles`
M:N bridge table associating employees with system security roles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `employee_id` | VARCHAR(32) | FK -> `employees.employee_id` | Composite PK part 1 |
| `role_id` | VARCHAR(32) | FK -> `roles.role_id` | Composite PK part 2 |
| `assigned_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Timestamp of assignment |

### 2.8 `user_accounts`
Authentication credentials, argon2/bcrypt password hashes, and active status.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | VARCHAR(32) | PRIMARY KEY | Format: `USR-000001` |
| `employee_id` | VARCHAR(32) | UNIQUE, FK -> `employees.employee_id` | Bound employee entity |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL | Corporate login handle (e.g. `eleanor.vance`) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Corporate email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt salted hash (max 72 bytes plain input) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account activity flag |
| `created_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `last_login` | TIMESTAMPTZ | YES | Last recorded authentication session |

### 2.9 `feedback_evidence`
M:N bridge binding verifiable evidence artifacts to 360° feedback entries.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `feedback_id` | VARCHAR(32) | FK -> `feedbacks.feedback_id` | Composite PK part 1 |
| `evidence_id` | VARCHAR(32) | FK -> `evidences.evidence_id` | Composite PK part 2 |
| `linked_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Timestamp of linkage |

### 2.10 `review_permissions`
Defines authorized 360° peer and stakeholder review assignments per cycle.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `permission_id` | VARCHAR(32) | PRIMARY KEY | Format: `RP-000001` |
| `review_cycle_id` | VARCHAR(32) | FK -> `review_cycles.cycle_id` | Bound review cycle |
| `subject_employee_id` | VARCHAR(32) | FK -> `employees.employee_id` | Employee being reviewed |
| `reviewer_employee_id`| VARCHAR(32) | FK -> `employees.employee_id` | Authorized reviewer |
| `relationship_type` | VARCHAR(30) | NOT NULL | `PEER`, `CROSS_FUNCTIONAL`, `STAKEHOLDER` |
| `granted_by` | VARCHAR(32) | FK -> `employees.employee_id` | Authorizing manager or HR partner |
| `granted_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Authorization grant timestamp |

### 2.11 `review_histories`
State-machine stage transitions audit log for performance reviews.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `history_id` | VARCHAR(32) | PRIMARY KEY | Format: `RH-000001` |
| `review_id` | VARCHAR(32) | FK -> `reviews.review_id` | Bound performance review |
| `previous_stage` | VARCHAR(50) | NOT NULL | Stage before transition |
| `new_stage` | VARCHAR(50) | NOT NULL | Stage after transition |
| `changed_by` | VARCHAR(32) | FK -> `employees.employee_id` | Modifying actor |
| `comments` | TEXT | | Stage transition notes |
| `changed_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Transition timestamp |

### 2.12 `development_activities`
Granular learning actions, certifications, or projects comprising an IDP.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `activity_id` | VARCHAR(32) | PRIMARY KEY | Format: `DA-000001` |
| `plan_id` | VARCHAR(32) | FK -> `development_plans.plan_id` | Parent development plan |
| `title` | VARCHAR(200) | NOT NULL | Activity headline / course name |
| `activity_type` | VARCHAR(50) | NOT NULL | `COURSE`, `MENTORSHIP`, `PROJECT`, `READING` |
| `resource_url` | VARCHAR(500) | | External course or documentation URL |
| `status` | VARCHAR(30) | DEFAULT 'NOT_STARTED' | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED` |
| `completed_date` | DATE | YES | Completion timestamp |
| `created_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### 2.13 `development_plan_approvals`
Dual-level governance approval tracking (Manager + HR Partner) for IDPs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `approval_id` | VARCHAR(32) | PRIMARY KEY | Format: `DPA-000001` |
| `plan_id` | VARCHAR(32) | FK -> `development_plans.plan_id` | Bound development plan |
| `approver_id` | VARCHAR(32) | FK -> `employees.employee_id` | Approving employee |
| `approval_role` | VARCHAR(30) | NOT NULL | `MANAGER`, `HR_PARTNER` |
| `decision` | VARCHAR(20) | NOT NULL | `APPROVED`, `REJECTED`, `CHANGES_REQUESTED` |
| `comments` | TEXT | | Governance justification |
| `decided_at` | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Timestamp of decision |

---

## 3. Ground Truth Evaluation Artifact (Non-Relational)

> [!IMPORTANT]
> **Ground Truth Isolation Guarantee**: Ground truth records (`ground_truth.json` and `ground_truth.csv`) are **offline evaluation benchmarks** stored exclusively in `generated_data/*/`. They are **NOT** a 24th relational database table.
> - The runtime anomaly detection engine does **not** read or access ground truth files.
> - Normal business operations, OKR calculations, review calibrations, and employee APIs never query ground truth.
> - Ordinary application APIs mask ground truth labels as `RESTRICTED_SECURITY_ROLE` for non-administrative users.
> - Ground truth is ingested strictly by evaluation verification harnesses (`backend/validators/runner.py`) after anomaly detection has completed to compute independent precision and recall metrics against the five injected negative scenarios.
