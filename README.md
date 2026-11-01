# YottaPerf: Enterprise Performance Management & Development Platform

[![CI / Automated Tests](https://img.shields.io/badge/tests-17%20passed-emerald)](https://github.com/usharani222/YottaPerf)
[![Validation Engine](https://img.shields.io/badge/validation-147k%20records%20PASSED-emerald)](https://github.com/usharani222/YottaPerf)
[![Reproducibility](https://img.shields.io/badge/seed-20261022%20verified-indigo)](https://github.com/usharani222/YottaPerf)
[![Architecture](https://img.shields.io/badge/schema-3NF%20PostgreSQL%20(23%20tables)-blue)](https://github.com/usharani222/YottaPerf)
[![License](https://img.shields.io/badge/license-MIT-slate)](LICENSE)

**YottaPerf** is an end-to-end, production-grade Employee Performance Management, OKR Tracking, 360° Feedback, Competency Evaluation, and Development Planning Platform built with FastAPI, PostgreSQL (SQLAlchemy 2.0 / Alembic), and Next.js 14 (TypeScript / Tailwind CSS).

The platform features deterministic synthetic data generation, an anomaly injection and detection engine, isolated ground-truth datasets, a 15-point multi-dimensional relational validation engine, immutable cryptographic audit logging, and role-based access control (RBAC).

---

## 1. Business Problem & Mission

Traditional enterprise performance management software suffers from three structural flaws:
1. **Disconnected OKRs:** Goal progress is often manually self-reported without source-verifiable metrics, creating inaccurate evaluations.
2. **Untraceable & Ineligible Feedback:** Reviews and feedback often lack verifiable evidence artifacts, or permit non-working-relationship peer assessments that bias ratings.
3. **Audit Vulnerability & Closed Cycle Tampering:** Review cycles and calibration scores are frequently adjusted retroactively without cryptographic audit trails.

**YottaPerf** solves these challenges by enforcing:
- **Strictly Derived Progress:** Key Result progress is mathematically computed from baseline, target, and current readings (supporting both increasing and decreasing metric directions with zero-denominator safeguards). Goal progress is computed as the strict weighted sum of its child Key Results.
- **Evidence-Based Check-Ins:** Every check-in update links verifiable evidence (e.g. PR links, documentation URLs, design specs).
- **Relational Integrity & DAG Hierarchy:** Reporting structures are validated against cycle graphs via depth-first search, preventing circular management hierarchies.
- **Closed-Cycle Immutability:** Closed review cycles unconditionally reject non-administrative modifications. Authorized administrative overrides produce an immutable audit event and preserve previous version snapshots.

---

## 2. Key Features

- **Organization Hierarchy & Manager Transfers:** Directed acyclic graph (DAG) traversal prevents circular reporting loops. Tracks complete historical manager assignments with effective date ranges.
- **Measurable Goals & Key Results (OKRs):** Multi-tenant goal setting with weighted Key Results. Strictly computed progress formulas handle increasing metrics (`((curr - base) / (tgt - base)) * 100`) and decreasing metrics (`((base - curr) / (base - tgt)) * 100`).
- **Periodic Check-Ins & Evidence Vault:** Check-ins record employee updates, manager feedback, blockers, next steps, and verified evidence links (`CODE_PR`, `DOCUMENT`, `DASHBOARD`, `DEPLOYMENT`).
- **360° Competency & Feedback Workflow:** Supports `SELF`, `MANAGER`, and `PEER` feedback across 12 standardized competencies (e.g., Technical Excellence, System Architecture, Leadership, Ownership). Conflicting feedback is preserved transparently rather than silently overwritten.
- **Performance Review Calibration:** Transparent scoring engine with configurable weight model (Default: 50% Goal Achievement, 30% Competency Evaluation, 20% Feedback Evaluation). Formal stage transitions: `DRAFT` &rarr; `SELF_REVIEW_PENDING` &rarr; `MANAGER_REVIEW_PENDING` &rarr; `HR_REVIEW_PENDING` &rarr; `APPROVED` &rarr; `COMPLETED`. Employees are strictly barred from self-approving reviews.
- **Individual Development Plans (IDPs):** Automatic competency gap detection recommending actionable learning resources, milestone dates, and dual-level approval workflows (Manager + HR).
- **Anomaly Detection & Exception Management:** Dedicated Anomaly Center for identifying and remediating business anomalies with explicit ground-truth matching.
- **Immutable Security & Audit Ledger:** Captures entity diffs (`previous_state` &rarr; `new_state`), actor IDs, client IP addresses, review cycles, and override reasons.
- **Role-Based Access Control (RBAC):** Five distinct roles (`EMPLOYEE`, `MANAGER`, `HR_PARTNER`, `IT_OPS`, `ADMIN`) enforced via JWT tokens and API-level dependency policies.

---

## 3. Technology Stack

| Layer | Technologies | Description |
|---|---|---|
| **Backend API** | Python 3.11+ / 3.12, FastAPI 0.110+, Pydantic v2 | High-throughput asynchronous REST API |
| **ORM & Database** | PostgreSQL 16, SQLAlchemy 2.0, Alembic | 3NF normalized schema with 23 tables |
| **Frontend UI** | Next.js 14+ (App Router), TypeScript, React, Tailwind CSS | Enterprise responsive dark-mode portal |
| **Data Visualization** | Recharts, Lucide Icons | Responsive interactive charts and metrics |
| **Data Engineering** | Faker, NumPy, Pandas | Deterministic generator engine (Seed: `20261022`) |
| **Validation Engine** | Custom 15-Point Multi-Dimensional Auditor | Validates PK, FK, DAG, Enums, Math, Lifecycles |
| **Testing** | Pytest, FastAPI TestClient | 17 comprehensive unit/integration test suites |
| **Infrastructure** | Docker, Docker Compose | Multi-container deployment configuration |

---

## 4. Database Architecture & Relationships

The database is normalized to Third Normal Form (3NF) comprising **23 relational tables**, explicit foreign-key constraints, and deterministic ID conventions:

```
[Employee] 1 ──── * [Goal] 1 ──── * [KeyResult]
    │                     │
    │ 1 ──── * [CheckIn] ─┘
    │             │
    │             * 1 [Evidence]
    │
    │ 1 ──── * [Feedback] * ──── 1 [Competency]
    │             │
    │ 1 ──── * [Review] 1 ──── * [DevelopmentPlan]
    │                                   │
    │ 1 ──── * [EmployeeManagerHistory] * ──── 1 [DevelopmentActivity]
    │
    * ──── * [Role] (via [EmployeeRole] bridge)
```

### Deterministic ID Conventions
- **Employee:** `EMP-000001`
- **Manager:** `MGR-000001`
- **Review Cycle:** `CYCLE-2026-H1`
- **Goal:** `GOAL-EMP-000001-001`
- **Key Result:** `KR-GOAL-EMP-000001-001-01`
- **Check-In:** `CHK-000001`
- **Feedback:** `FB-000001`
- **Review:** `REV-2026-000001`
- **Development Plan:** `DP-000001`
- **Evidence:** `EVD-000001`
- **Anomaly:** `ANO-000001`
- **Audit Event:** `AUD-000001`

Detailed documentation:
- [Architecture Overview](docs/architecture.md)
- [Database Relationships & ERD](docs/database_relationships.md)
- [Data Dictionary (23 Tables)](docs/data_dictionary.md)
- [Business Rules & Math Formulas](docs/business_rules.md)
- [Anomaly Catalog](docs/anomaly_catalog.md)

---

## 5. Anomaly Injection Engine & Ground Truth

The platform features an isolated anomaly injection module that injects realistic edge-case irregularities without corrupting baseline referential integrity.

### The Five Mandatory Injected Anomalies:
1. `GOAL_OWNER_MISMATCH`: A goal assigned to an employee differs from the parent goal's true owner.
2. `INVALID_PROGRESS`: Progress exceeds allowable scale (>100% or invalid range) without an approved override rationale.
3. `INVALID_REVIEWER`: Feedback submitted by a reviewer without an eligible reporting or collaborative relationship.
4. `CLOSED_CYCLE_MODIFICATION`: Modification attempted on a closed review cycle without an administrative audit correction event.
5. `UNTRACEABLE_FEEDBACK`: Subjective feedback recorded without verifiable evidence or sufficient traceability metadata.

**Ground-Truth Isolation:** Deliberately injected anomalies are stored in `ground_truth.csv` and `ground_truth.json` with expected resolution directives. Ground-truth metadata is strictly sequestered from standard API input features.

---

## 6. Automated Validation Engine

The 15-point automated validation engine scans datasets and database records to guarantee absolute data integrity:

| Check | Validation Item | Description | Status |
|---|---|---|---|
| **A** | Primary Key Uniqueness | Ensures all entity IDs are unique and strictly formatted | `PASSED` |
| **B** | Foreign Key Integrity | Validates all parent-child references exist | `PASSED` |
| **C** | Allowed Enum Values | Checks lifecycle stages, roles, priorities, directions | `PASSED` |
| **D** | Date Ordering | Validates `start_date` &le; `end_date` &le; `submission_deadline` | `PASSED` |
| **E** | Goal & Key Result Consistency | Reconciles child KR links and parent goal references | `PASSED` |
| **F** | Review Cycle Consistency | Validates cycle state rules and submission windows | `PASSED` |
| **G** | Manager Hierarchy DAG | DFS traversal verifies no circular reporting loops | `PASSED` |
| **H** | Duplicate Record Detection | Scans for semantic duplicate tuples | `PASSED` |
| **I** | Progress Calculation Correctness | Recalculates KR formulas against stored values | `PASSED` |
| **J** | Weighted Score Reconciliation | Verifies goal progress = &sum;(KR progress &times; KR weight) | `PASSED` |
| **K** | Review Lifecycle State Machine | Validates valid transition paths | `PASSED` |
| **L** | Role & Permission Rules | Enforces RBAC constraints and self-approval bans | `PASSED` |
| **M** | Audit History Completeness | Validates audit trail for all modifications | `PASSED` |
| **N** | Development Plan Approvals | Verifies manager and HR dual-approval rules | `PASSED` |
| **O** | Anomaly & Ground-Truth Consistency| Verifies 100% detection rate of injected anomalies | `PASSED` |

Full audit details: [docs/validation_report.md](docs/validation_report.md)

---

## 7. Installation & Quick Start

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ or 20+ and npm
- PostgreSQL 15+ (or Docker)
- Git

### Port Allocation
To avoid collisions with standard local services, YottaPerf uses the following dedicated host ports:
- **Frontend Portal:** `http://localhost:3002`
- **Backend REST API:** `http://localhost:8001`
- **PostgreSQL Database:** `localhost:5434` (mapped to internal `5432`)

---

### Option A: Running via Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/usharani222/YottaPerf.git
   cd YottaPerf
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```

3. **Build and start all services:**
   ```bash
   docker compose up --build -d
   ```

4. **Verify running containers:**
   ```bash
   docker compose ps
   ```

5. **Access Application:**
   - Frontend UI: [http://localhost:3002](http://localhost:3002)
   - Interactive Swagger API: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### Option B: Local Development Setup

#### 1. Backend Setup

```bash
# Navigate to project root
cd YottaPerf

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations with Alembic
alembic -c backend/migrations/alembic.ini upgrade head

# Start Backend API server on Port 8001
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd YottaPerf/frontend

# Install Node dependencies
npm install

# Build Next.js application
npm run build

# Start Next.js development server on Port 3002
PORT=3002 npm run dev
```

---

## 8. Synthetic Data Generation & Reproducibility

The platform includes a deterministic synthetic generation engine using a fixed seed (`20261022`).

### 1. Generate Starter Dataset (50 Emps, 10 Mgrs, 150 Goals)
```bash
python3 -m backend.generator.runner --mode starter --seed 20261022 --output-dir generated_data/starter
```

### 2. Generate Full Baseline Dataset (3,000 Emps, 500 Mgrs, 10,000 Goals, 20,000 Check-ins)
```bash
python3 -m backend.generator.runner --mode full --seed 20261022 --output-dir generated_data/full
```

### 3. Load Generated Data directly into PostgreSQL
```bash
python3 -m backend.generator.runner --mode starter --seed 20261022 --insert-db
```

### 4. Reproducibility Guarantee
Running the generator twice with identical seeds produces identical file hashes and dataset manifests:
```bash
# Verify bit-for-bit SHA-256 reproducibility
python3 -m backend.generator.runner --mode starter --seed 20261022 --output-dir run1
python3 -m backend.generator.runner --mode starter --seed 20261022 --output-dir run2

# Compare dataset manifest checksums (output should be identical):
cat run1/manifest.json | grep checksum
cat run2/manifest.json | grep checksum
```

---

## 9. Running Validation Engine & Automated Tests

### Run 15-Point Automated Validation Audit
```bash
# Validate Starter Dataset
python3 -m backend.validators.runner --dataset-dir generated_data/starter

# Validate Full Dataset (147,477 records)
python3 -m backend.validators.runner --dataset-dir generated_data/full
```

### Run Pytest Test Suite (17 Comprehensive Integration Tests)
```bash
pytest -v
```

**Test Coverage Summary:**
1. `test_01_employee_creation` &mdash; Employee profile persistence and field constraints.
2. `test_02_manager_assignment` &mdash; Manager link assignment and transfer tracking.
3. `test_03_circular_hierarchy_rejection` &mdash; DFS cycle detection rejecting circular reporting loops.
4. `test_04_goal_creation` &mdash; Goal creation with employee and review cycle validation.
5. `test_05_key_result_progress_calculation` &mdash; Mathematical calculation for increasing and decreasing metrics.
6. `test_06_weighted_goal_progress_calculation` &mdash; Reconciliation of goal progress from weighted Key Results.
7. `test_07_invalid_progress_rejection` &mdash; Rejection of out-of-scale progress updates.
8. `test_08_and_09_checkin_creation_and_evidence_linking` &mdash; Check-in recording with attached evidence records.
9. `test_10_reviewer_relationship_validation` &mdash; Reviewer relationship eligibility verification.
10. `test_11_conflicting_feedback_handling` &mdash; Non-destructive recording of multi-reviewer conflicting evaluations.
11. `test_12_review_score_calculation` &mdash; Configurable scoring formula (50% Goals / 30% Competencies / 20% Feedback).
12. `test_13_review_approval_permissions` &mdash; Enforcement of manager/HR approval steps and employee self-approval ban.
13. `test_14_closed_review_cycle_modification_rejection` &mdash; Rejection of closed cycle modifications without audit event.
14. `test_15_audit_history_creation` &mdash; Generation of cryptographic audit snapshots.
15. `test_16_development_plan_approval` &mdash; Dual manager & HR approval lifecycle for development plans.
16. `test_17_18_19_validation_engine_integrity_and_anomalies` &mdash; Referential integrity and 100% anomaly detection.
17. `test_20_fixed_seed_reproducibility` &mdash; Bit-for-bit SHA-256 reproducibility check.

---

## 10. Default User Accounts (RBAC)

When seeded, the following accounts are initialized with password `Password123!`:

| Username | Role | Full Name | Title |
|---|---|---|---|
| `eleanor.vance` | `ADMIN`, `MANAGER` | Eleanor Vance | Chief Executive Officer |
| `marcus.chen` | `HR_PARTNER` | Marcus Chen | VP of People Operations |
| `devon.ross` | `IT_OPS` | Devon Ross | Director of Cloud Engineering |
| `sarah.jenkins` | `MANAGER` | Sarah Jenkins | Engineering Manager |
| `david.miller` | `EMPLOYEE` | David Miller | Senior Backend Engineer |

---

## 11. REST API Documentation

FastAPI auto-generates interactive OpenAPI documentation:
- **Swagger UI:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc:** [http://localhost:8001/redoc](http://localhost:8001/redoc)

### Core Endpoints

#### Authentication
- `POST /api/auth/login` &mdash; Obtain JWT bearer token.
- `GET /api/auth/me` &mdash; Retrieve active user profile & roles.

#### Organization & Employees
- `GET /api/employees` &mdash; List employees with pagination and department filters.
- `POST /api/employees` &mdash; Create employee profile.
- `GET /api/organization/hierarchy` &mdash; Return complete organization tree.
- `POST /api/organization/transfer/{id}` &mdash; Transfer employee manager with cycle detection.

#### Goals & OKRs
- `GET /api/goals` &mdash; Query goals by cycle, owner, or status.
- `POST /api/goals` &mdash; Create new goal.
- `GET /api/goals/{id}/history` &mdash; Retrieve immutable audit snapshots for a goal.
- `POST /api/goals/{id}/key-results` &mdash; Add measurable Key Result.
- `PUT /api/key-results/{id}` &mdash; Update current reading with automatic progress recalculation.

#### Reviews & Calibration
- `GET /api/reviews` &mdash; List performance reviews by cycle and stage.
- `POST /api/reviews/{id}/transition` &mdash; Transition review stage (`SELF_REVIEW` &rarr; `MANAGER_REVIEW` &rarr; `HR_REVIEW` &rarr; `APPROVED`).
- `POST /api/reviews/{id}/calculate` &mdash; Recalculate transparent score from underlying OKRs and ratings.

#### Exceptions & Administration
- `GET /api/anomalies` &mdash; Query detected anomalies and severity.
- `POST /api/anomalies/{id}/resolve` &mdash; Remediate anomaly with resolution notes and audit entry.
- `POST /api/admin/generate-data` &mdash; Trigger synthetic data pipeline (`starter` or `full`).
- `POST /api/admin/validate-data` &mdash; Execute 15-point validation engine and return audit report.

---

## 12. Synthetic Data Provenance & Ethics

- **Zero PII:** 100% of employee names, emails, job histories, and feedback comments are deterministically generated by the synthetic generator module using pseudo-random seeds.
- **No External Data Scraping:** The platform does not use, store, or redistribute any real-world proprietary employee information.
- **Compliance:** Built in compliance with synthetic data standards for enterprise benchmarking and software evaluations.

---

## 13. Project Structure

```
YottaPerf/
├── backend/
│   ├── app/
│   │   ├── api/             # 12 REST API route modules
│   │   ├── core/            # Config, Database connection, JWT security
│   │   ├── models/          # 23 SQLAlchemy 2.0 ORM models
│   │   ├── permissions/     # RBAC dependency guards
│   │   ├── schemas/         # Pydantic v2 validation schemas
│   │   ├── services/        # Business workflow logic services
│   │   └── main.py          # FastAPI application entrypoint
│   ├── generator/           # Deterministic synthetic data generator engine
│   ├── validators/          # 15-point automated validation engine
│   ├── tests/               # 17 Pytest test suites
│   ├── migrations/          # Alembic database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js 14 App Router (layout.tsx, page.tsx)
│   ├── components/          # Reusable UI components & 13 views
│   ├── services/            # Typed API client
│   ├── types/               # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── database/
│   ├── schema.sql           # PostgreSQL 3NF DDL schema
│   └── seed/                # SQL seed scripts
├── generated_data/
│   ├── starter/             # Starter dataset (CSV, JSON, SQL seed, ground_truth)
│   └── full/                # Full dataset (147k records, 3k employees, 10k goals)
├── docs/                    # Architecture, Data Dictionary, Business Rules, etc.
├── docker-compose.yml       # Production multi-container composition
├── .env.example             # Configuration template
├── pytest.ini               # Test configuration
├── .gitignore
└── README.md
```

---

## 14. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
