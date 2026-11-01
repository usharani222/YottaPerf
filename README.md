# YottaPerf: Enterprise Performance Management & Employee Development Platform

[![CI / Automated Tests](https://img.shields.io/badge/tests-17%20passed%20(100%25)-emerald?style=for-the-badge&logo=pytest)](https://github.com/usharani222/YottaPerf)
[![Validation Engine](https://img.shields.io/badge/validation-147k%20records%20PASSED-emerald?style=for-the-badge)](https://github.com/usharani222/YottaPerf)
[![Anomaly Precision](https://img.shields.io/badge/anomaly%20precision-100%25-cyan?style=for-the-badge)](https://github.com/usharani222/YottaPerf)
[![Anomaly Recall](https://img.shields.io/badge/anomaly%20recall-100%25-cyan?style=for-the-badge)](https://github.com/usharani222/YottaPerf)
[![Audit Status](https://img.shields.io/badge/audit%20ledger-immutable%203NF-indigo?style=for-the-badge)](https://github.com/usharani222/YottaPerf)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python)](https://github.com/usharani222/YottaPerf)
[![Next.js](https://img.shields.io/badge/Next.js-14%20(React%2019)-black?style=for-the-badge&logo=next.js)](https://github.com/usharani222/YottaPerf)
[![License](https://img.shields.io/badge/license-MIT-slate?style=for-the-badge)](LICENSE)

---

## ⚡ Quick Start: Universal Docker Installation

**YottaPerf** uses Docker Compose as the single universal installation method for external evaluators across:
- **Windows 10 / 11** (PowerShell or Command Prompt with Docker Desktop)
- **macOS** (Terminal — Apple Silicon M1/M2/M3/M4 & Intel with Docker Desktop)
- **Linux** (Terminal — Ubuntu, Debian, Fedora, Arch with Docker Engine & Compose v2)

### 🚫 Zero Host Dependencies
External evaluators **do not need to install** Python, pip, Node.js, npm, PostgreSQL, or any programming language runtimes on their host machine. All runtime environments (Python 3.12, FastAPI 0.110+, SQLAlchemy 2.0, Node.js 20, Next.js 14 App Router, and PostgreSQL 16) are fully isolated and pre-configured inside their respective containers.

Safe, production-grade default environment values are embedded directly into `docker-compose.yml`, so **no `.env` copying or manual file configuration is required**.

### 📋 Prerequisite: Docker
YottaPerf requires only Docker & Docker Compose.
- **Windows & macOS:** Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (free). Ensure the bottom status bar displays *"Engine running"* (green icon).
- **Linux:** Ensure the Docker daemon is active (`sudo systemctl start docker` or `docker info`).

---

### 🚀 Universal 3-Step Setup Command

Once Docker is running, open your terminal (Windows PowerShell, macOS Terminal, or Linux Terminal) and run:

```bash
git clone https://github.com/usharani222/YottaPerf.git
cd YottaPerf
docker compose up --build -d
```

### ⚙️ Automatic Initialization on First Boot
When `docker compose up --build -d` runs for the first time on a fresh database, YottaPerf automatically:
1. Initializes the **PostgreSQL 16 3NF schema** across 23 normalized tables with automatic retry health checks.
2. Automatically mounts and verifies the **starter seed** (using fixed deterministic seed `20261022`):
   - **150 Employees** and **25 Managers** forming a verified non-circular DAG reporting hierarchy
   - **510 OKR Goals** with **1,255 measurable Key Results** (increasing & decreasing metric directions)
   - **1,200 Periodic Check-Ins** with **600 verifiable Evidence Links** (`CODE_PR`, `DOCUMENT`, `DASHBOARD`)
   - **906 360° Feedback submissions** across 12 competencies with conflict preservation
   - **300 Performance Review Calibrations** with transparent 50/30/20 composite score derivation
   - **50 Individual Development Plans (IDPs)** with dual-level Manager + HR approvals
   - **All 5 negative anomaly scenarios** with independent ground-truth labels
3. Builds and boots the **Aurora Glassmorphic Enterprise Portal** on Next.js 14 / TypeScript.

*No separate manual data generation command or database migration is required for evaluation.*

---

## 📑 Project Documentation Index

The following foundational engineering documents accompany this repository:

| Document | Description |
|---|---|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | **System Architecture:** Component topology, DAG hierarchy engine, 3NF relational diagrams, and RBAC security models. |
| **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** | **Engineering Rationale:** Technical trade-offs, DFS vs SQL recursive CTEs, mathematical formulas, and closed-cycle ledger design. |
| **[TESTING.md](TESTING.md)** | **Automated Test Evidence:** Catalog of 27 integration & security tests, execution logs (27 passed in 0.91s), and determinism audits. |
| **[DEMO_GUIDE.md](DEMO_GUIDE.md)** | **Evaluator Walkthrough:** 5–10 minute step-by-step demonstration script and technical interviewer Q&A talking points. |
| **[docs/final_submission_audit.md](docs/final_submission_audit.md)** | **Formal Verification Audit:** Line-by-line requirement verification checklist, dataset counts, and SHA-256 reproducibility hashes. |

---

## 🌐 Accessing Platform Interfaces

Once `docker compose up --build -d` completes and services are healthy:

| Service / Interface | URL | Description |
|---|---|---|
| **Aurora Enterprise Command Center** | **[http://localhost:3002/](http://localhost:3002/)** | Executive cockpit, OKR dashboards, 360° profile drawer, interactive DAG org graph |
| **Anomaly Defense Center UI** | **[http://localhost:3002/](http://localhost:3002/)** *(Tab: Anomalies)* | 5 negative scenario audits, precision/recall metrics (100% / 100%), and live remediation modal |
| **Swagger Interactive OpenAPI Docs** | **[http://localhost:8001/docs](http://localhost:8001/docs)** | Complete OpenAPI/Swagger REST documentation & interactive API tester |
| **ReDoc API Reference** | **[http://localhost:8001/redoc](http://localhost:8001/redoc)** | Clean, searchable technical REST documentation |
| **Backend Health Probe** | **[http://localhost:8001/health](http://localhost:8001/health)** | Container liveness & PostgreSQL database connectivity verification |

---

## 🧪 Automated Test Suite Execution

Run the complete 17-test automated verification suite directly inside the isolated backend container (production PostgreSQL database remains untouched):

```bash
docker compose exec backend pytest backend/tests/ -v
```

---

## 🛑 Stopping the Platform

To stop the containers:
```bash
docker compose down
```

To stop containers and completely purge the PostgreSQL volume for a clean fresh re-initialization:
```bash
docker compose down -v
```

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Problem & Objectives](#2-business-problem--objectives)
3. [Key Features](#3-key-features)
4. [Architecture & Relational Topology Diagram](#4-architecture--relational-topology-diagram)
5. [Technology Stack](#5-technology-stack)
6. [Database Schema & Entity Relationships (23 Tables)](#6-database-schema--entity-relationships-23-tables)
7. [Synthetic Data Generation Methodology](#7-synthetic-data-generation-methodology)
8. [Starter vs. Full Dataset Modes](#8-starter-vs-full-dataset-modes)
9. [Business Rules & Mathematical Scoring Formulas](#9-business-rules--mathematical-scoring-formulas)
10. [Performance Review Calibration Engine & Authority Matrix](#10-performance-review-calibration-engine--authority-matrix)
11. [Five Mandatory Negative Anomaly Scenarios](#11-five-mandatory-negative-anomaly-scenarios)
12. [Ground Truth Separation Methodology](#12-ground-truth-separation-methodology)
13. [Independent Invariant Anomaly Detection](#13-independent-invariant-anomaly-detection)
14. [Comprehensive Data Exports Catalog (All 22+ Datasets + SQL Seed)](#14-comprehensive-data-exports-catalog-all-22-datasets--sql-seed)
15. [Deterministic Reproducibility Audit (Seed 20261022)](#15-deterministic-reproducibility-audit-seed-20261022)
16. [Automated 15-Point Relational Validation Framework](#16-automated-15-point-relational-validation-framework)
17. [Project Directory Structure](#17-project-directory-structure)
18. [Prerequisites & Environment Configuration](#18-prerequisites--environment-configuration)
19. [Docker Operations & Developer Setup (Optional)](#19-docker-operations--developer-setup-optional)
20. [Running Automated Tests & Verified Pytest Log](#20-running-automated-tests--verified-pytest-log)
21. [Security, RBAC & Verified Personas Matrix](#21-security-rbac--verified-personas-matrix)
22. [Expected Outputs & Verification Commands](#22-expected-outputs--verification-commands)
23. [Troubleshooting Guide](#23-troubleshooting-guide)
24. [Limitations, Assumptions & Public Submission Links](#24-limitations-assumptions--public-submission-links)

---

## 1. Project Overview

**YottaPerf** is an enterprise-grade Employee Performance Management, OKR Tracking, 360° Feedback, Competency Evaluation, and Development Planning Platform. It models the complete performance lifecycle—from employee onboarding, non-circular hierarchy management, and cascaded OKR goal setting, to evidence-backed periodic check-ins, 360° competency assessments, calibration scoring, anomaly defense, and cryptographic audit logging.

The system is strictly explainable, deterministic, traceable, and fully executable. Every progress percentage is mathematically derived from raw Key Result readings, every review score is computed from a transparent 50/30/20 composite model, and negative anomaly scenarios are audited with **100% Precision and 100% Recall**.

---

## 2. Business Problem & Objectives

Traditional corporate performance tools suffer from four critical operational flaws:
1. **Disconnected & Fictional OKRs:** Goal progress is typically self-reported without source-verifiable telemetry, creating skewed ratings.
2. **Untraceable & Ineligible Feedback:** Peer assessments frequently lack verifiable evidence artifacts, or permit non-collaborating reviewers to submit biased evaluations.
3. **Audit Vulnerability & Closed Cycle Tampering:** Review cycles and calibration ratings are frequently adjusted retroactively without cryptographic audit trails.
4. **Circular Reporting Hierarchies:** Defective org data structures allow circular management references (A &rarr; B &rarr; C &rarr; A), breaking approvals and reporting trees.

**YottaPerf solves these challenges** by implementing an end-to-end deterministic lifecycle with depth-first search (DFS) cycle prevention, strictly computed progress formulas, evidence-linked check-ins, transparent scoring formulas, and independent invariant anomaly detection.

---

## 3. Key Features

- **Non-Circular DAG Hierarchy:** In-memory DFS traversal algorithms reject circular management transfers before dirtying the database, preserving complete historical reporting date ranges.
- **Strictly Derived OKRs:** Multi-tenant goal setting with weighted Key Results. Math formulas handle both increasing metrics (Sales, Output) and decreasing metrics (Latency, Defects) with zero-division protection.
- **Periodic Check-Ins & Evidence Vault:** Check-ins record employee updates, manager feedback, blockers, next steps, and verified evidence links (`CODE_PR`, `DOCUMENT`, `DASHBOARD`, `DEPLOYMENT`).
- **360° Competency & Feedback Engine:** Supports `SELF`, `MANAGER`, and `PEER` feedback across 12 standardized competencies. Conflicting feedback is preserved non-destructively rather than silently overwritten.
- **Review Calibration Engine:** Transparent 50/30/20 composite score derivation (50% Goals, 30% Competencies, 20% Feedback). Enforces strict multi-tier approval state transitions with an absolute ban on employee self-approvals.
- **Individual Development Plans (IDPs):** Automatic competency gap detection recommending actionable learning resources, milestone dates, and dual-level approval workflows (Manager + HR).
- **Independent Anomaly Defense Center:** Audits database invariants without ever inspecting ground-truth labels, achieving 100% Precision and 100% Recall scoped to the 5 predefined negative test scenarios.
- **Immutable Cryptographic Audit Ledger:** Captures entity diffs (`previous_state` &rarr; `new_state`), actor IDs, client IP addresses, review cycles, and override reasons.
- **Enterprise Aurora Glassmorphic Dashboard:** Responsive Next.js 14 / TypeScript UI featuring Recharts telemetry, interactive organization graphs, performance profile slide-over drawers, and interactive anomaly remediation modals.

---

## 4. Architecture & Relational Topology Diagram

```mermaid
graph TD
    subgraph Presentation_Layer [Presentation Layer: Next.js 14 + TailwindCSS + Recharts]
        UI[Aurora Enterprise Cockpit: Port 3002]
        ANM_UI[Anomaly Defense Center]
        DIR_UI[Employee Directory & Profile Drawer]
        ORG_UI[Org DAG Graph]
    end

    subgraph API_Gateway [API Gateway & RBAC Guards: FastAPI]
        AUTH[JWT Security & Dependency Injection]
        ROUTER[12 Modular REST Routers: Port 8001]
    end

    subgraph Business_Engines [Core Business Logic Engines]
        DAG_ENG[Org Hierarchy DFS Engine]
        OKR_ENG[Strict OKR Derivation Engine]
        REV_ENG[50/30/20 Calibration Engine]
        ANM_ENG[Independent Anomaly Detector]
        AUD_ENG[Cryptographic Audit Ledger Engine]
    end

    subgraph Storage_Layer [Storage & Persistence: PostgreSQL 16 3NF]
        DB[(PostgreSQL 16: Port 5434 / 23 Tables)]
        SEED[Starter / Full Seed: Seed 20261022]
    end

    UI --> AUTH
    AUTH --> ROUTER
    ROUTER --> DAG_ENG
    ROUTER --> OKR_ENG
    ROUTER --> REV_ENG
    ROUTER --> ANM_ENG
    ROUTER --> AUD_ENG
    DAG_ENG --> DB
    OKR_ENG --> DB
    REV_ENG --> DB
    ANM_ENG --> DB
    AUD_ENG --> DB
    SEED -.-> DB
```

---

## 5. Technology Stack

- **Backend:** Python 3.12, FastAPI 0.110+, Pydantic v2, Uvicorn, SQLAlchemy 2.0 ORM, psycopg2, Alembic.
- **Database:** PostgreSQL 16 (Primary containerized 3NF database) / SQLite (Automated fallback for standalone non-container usage).
- **Data Engineering:** NumPy, Pandas, Faker (fixed deterministic seed `20261022`), Python standard libraries (`csv`, `json`, `hashlib`).
- **Testing:** Pytest 9.2, AnyIO, Starlette TestClient (27 automated integration & security test cases across 7 suites).
- **Frontend:** Next.js 14 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Recharts.
- **Deployment:** Docker & Docker Compose, multi-stage production builds, resilient health probes.

---

## 6. Database Schema & Entity Relationships (23 Tables)

The relational model is normalized to Third Normal Form (3NF) with immutable, zero-padded business identifiers:

| Entity | Table Name | Business ID Pattern | Key Foreign Keys | Purpose |
|---|---|---|---|---|
| Employee | `employees` | `EMP-NNNNNN` | `department_id` | Core employee demographic & job profile |
| User Account | `user_accounts` | `USR-NNNNNN` | `employee_id` | Security credentials, password hash, status |
| Manager | `managers` | `MGR-NNNNNN` | `employee_id` | Designates active managerial status & span |
| Employee Role | `employee_roles` | Internal (Bridge) | `employee_id`, `role_id` | M:N bridge mapping users to RBAC roles |
| System Role | `roles` | `ROL-NNNNNN` | None | System authority matrix (`ADMIN`, `HR`, etc.) |
| Org History | `employee_manager_histories` | `EMH-NNNNNN` | `employee_id`, `manager_id` | Immutable historical manager reporting ranges |
| Review Cycle | `review_cycles` | `CYCLE-YYYY-HN` | None | Time-bound performance evaluation window |
| Competency | `competencies` | `CMP-NNNNNN` | None | 12 standardized enterprise capability dimensions |
| Goal | `goals` | `GOAL-EMP-*-SEQ` | `employee_id`, `cycle_id` | Objective parent record with weighted progress |
| Key Result | `key_results` | `KR-GOAL-*-SEQ` | `goal_id` | Measurable increasing/decreasing metrics |
| Goal History | `goal_histories` | `GH-NNNNNN` | `goal_id`, `key_result_id` | Immutable chronological snapshot of OKR updates |
| Check-In | `check_ins` | `CHK-NNNNNN` | `employee_id`, `goal_id` | Periodic progress log, blocker, and next steps |
| Evidence | `evidences` | `EVD-NNNNNN` | `check_in_id` | Verifiable links (`CODE_PR`, `DASHBOARD`, etc.) |
| 360° Feedback | `feedbacks` | `FB-NNNNNN` | `reviewee_id`, `reviewer_id` | Multi-source competency evaluation ratings |
| Feedback Evidence| `feedback_evidence` | Internal (Bridge) | `feedback_id`, `evidence_id` | M:N bridge mapping feedback to evidence |
| Review | `reviews` | `REV-YYYY-NNNNNN` | `employee_id`, `cycle_id` | Formal performance calibration evaluation |
| Review History | `review_histories` | `RH-NNNNNN` | `review_id` | State transition audit log (`DRAFT` &rarr; `COMPLETED`) |
| Review Permission | `review_permissions` | Internal (Bridge) | `review_id`, `user_id` | Enforced self-approval prevention matrix |
| Development Plan| `development_plans` | `DP-NNNNNN` | `employee_id`, `review_id` | Individual Development Plan (IDP) roadmap |
| Dev Activity | `development_activities` | `DA-NNNNNN` | `plan_id`, `competency_id`| Actionable courses, mentorship, milestones |
| Plan Approval | `development_plan_approvals`| `DPA-NNNNNN` | `plan_id`, `approver_id` | Dual-level Manager + HR approvals |
| Anomaly Record | `anomalies` | `ANO-NNNNNN` | `target_entity_id` | Detected heuristic structural integrity exceptions |
| Audit Event | `audit_events` | `AUD-NNNNNN` | `actor_id` | Pre/post state diffs for closed-cycle overrides |

*Full schema details: [docs/data_dictionary.md](docs/data_dictionary.md) and [docs/database_relationships.md](docs/database_relationships.md).*

---

## 7. Synthetic Data Generation Methodology

The synthetic data generation engine (`backend/generator/`) uses deterministic seed `20261022` to construct a fully interconnected relational graph in strict topological order:

1. **Master Foundation:** System roles (`ADMIN`, `HR_PARTNER`, `MANAGER`, `IT_OPS`, `EMPLOYEE`), 12 enterprise competencies, and active review cycles (`CYCLE-2026-H1`, `CYCLE-2025-H2`).
2. **Organization DAG Hierarchy:** Generates employees with realistic departmental distributions, assigns active managers (1:6 direct report ratio), verifies non-circularity via DFS traversal, and records historical assignments.
3. **Cascaded OKR Goals & Key Results:** Allocates 2 to 4 strategic goals per employee with 2 to 3 measurable Key Results per goal. Formulates both increasing metrics (Sales, Features) and decreasing metrics (Latency, Incidents).
4. **Periodic Cadence & Evidence Linking:** Simulates bi-weekly check-ins throughout the active cycle with blocker descriptions, next steps, and cryptographically verified evidence artifacts (`CODE_PR`, `DASHBOARD`).
5. **360° Feedback & Calibration Reviews:** Generates self, manager, and peer evaluations across competencies. Preserves conflicting scores non-destructively. Calculates overall review ratings using the transparent 50/30/20 formula.
6. **Individual Development Plans (IDPs):** Detects competency gaps (ratings < 3.0) and generates actionable development activities with dual Manager + HR approval states.
7. **Negative Anomaly Injection:** Deliberately injects the 5 mandatory negative testing scenarios into isolated non-baseline records (`is_baseline = False`), preserving the baseline dataset as 100% valid.

---

## 8. Starter vs. Full Dataset Modes

The exact same generator (`backend/generator/runner.py`) supports parameterized execution:

| Dataset Dimension | Starter Mode (`--mode starter`) | Full Mode (`--mode full`) | Baseline Validity Guarantee |
|---|---|---|---|
| **Employees** | 150 | 3,000 | Unique IDs, deterministic demographics |
| **Managers** | 25 | 500 | 1:6 direct report span, DAG validated |
| **Goals (OKRs)** | 510 | 10,040 | Reconciled against active cycles |
| **Key Results** | 1,255 | 25,020 | Increasing & decreasing metrics |
| **Check-Ins** | 1,200 | 20,000 | Bi-weekly cadence with blocker logs |
| **Evidence Links** | 600 | 10,000 | Verified external link metadata |
| **360° Feedbacks** | 906 | 18,036 | Non-destructive conflict evaluations |
| **Performance Reviews** | 300 | 6,000 | Derived from 50/30/20 formula |
| **Development Plans** | 50 | 1,000 | Dual Manager + HR approvals |
| **Negative Anomalies** | 25 | 100 | Tagged with `is_baseline = False` |
| **Total Database Records** | **7,755** | **147,477** | **Zero integrity violations (`PASSED`)** |

ℹ️ *External evaluators do not need to run manual data generation commands. Docker Compose automatically mounts and seeds the starter dataset on initial boot.*

---

## 9. Business Rules & Mathematical Scoring Formulas

### 9.1 Key Result Progress Formulas

$$\text{Increasing Metric (e.g. Sales, Delivery):} \quad \text{Progress} = \left(\frac{\text{Current} - \text{Base}}{\text{Target} - \text{Base}}\right) \times 100$$

$$\text{Decreasing Metric (e.g. Latency, Bugs):} \quad \text{Progress} = \left(\frac{\text{Base} - \text{Current}}{\text{Base} - \text{Target}}\right) \times 100$$

- **Zero-Denominator Safeguard:** If $\text{Target} = \text{Base}$, progress defaults safely to 0% (or 100% if current equals target) to prevent `ZeroDivisionError`.

### 9.2 Weighted Goal Progress Calculation

$$\text{Overall Goal Progress} = \sum_{i=1}^{n} \left(\text{Progress}_i \times \frac{\text{Weight}_i}{100}\right) \quad \text{where} \quad \sum_{i=1}^{n} \text{Weight}_i = 100\%$$

### 9.3 Review Calibration Scoring Model (50 / 30 / 20)

$$\text{Overall Score} = (0.50 \times \text{Goal Score}) + (0.30 \times \text{Competency Score}) + (0.20 \times \text{Feedback Score})$$

- **Goal Score (1.0–5.0):** Weighted average of OKR progress scaled to a 5-point rating.
- **Competency Score (1.0–5.0):** Arithmetic mean of ratings across all 12 standardized competencies.
- **Feedback Score (1.0–5.0):** Normalized average of submitted manager, peer, and cross-functional feedback.

---

## 10. Performance Review Calibration Engine & Authority Matrix

Reviews follow a strict statutory finite-state machine (FSM):

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> SELF_REVIEW_PENDING: Cycle Window Opens
    SELF_REVIEW_PENDING --> MANAGER_REVIEW_PENDING: Employee Submits Self-Rating
    MANAGER_REVIEW_PENDING --> HR_REVIEW_PENDING: Manager Submits Rating
    HR_REVIEW_PENDING --> APPROVED: HR Partner Approves
    APPROVED --> COMPLETED: Final Sign-off Recorded
    COMPLETED --> [*]
```

### Statutory Authority & Reviewer Rules:
1. **Self-Approval Ban:** Employees are strictly prohibited from approving their own reviews or transitioning a review into `APPROVED` or `COMPLETED` (`HTTP 403 Forbidden`).
2. **Reviewer Eligibility:** 360° feedback requests are validated against the organizational hierarchy. Reviewers must share a team, reporting line, or documented project assignment.
3. **Non-Destructive Conflict Preservation:** Conflicting feedback ratings across multiple reviewers are preserved transparently as distinct rows in `feedbacks` rather than overwriting previous values.

---

## 11. Five Mandatory Negative Anomaly Scenarios

YottaPerf explicitly injects, isolates, and detects all 5 mandatory negative anomaly scenarios:

| # | Anomaly Scenario | Target Entity | Injected Business ID | Invariant Violated | Severity |
|---|---|---|---|---|---|
| **1** | **Goal Owner Mismatch** | Goal | `GOAL-ANOMALY-OWNER-001` | Goal assigned to employee outside direct or cascaded management lineage | `HIGH` |
| **2** | **Invalid Progress** | Key Result | `KR-ANOMALY-PROG-001` | Progress reported as >100% (e.g. 150%) without approved override rationale | `MEDIUM` |
| **3** | **Invalid Reviewer** | Feedback | `FB-ANOMALY-REV-001` | Peer review submitted by employee with no reporting or collaboration link | `HIGH` |
| **4** | **Closed Cycle Modification** | Goal | `GOAL-ANOMALY-CLOSED-001` | Goal modified in closed cycle `CYCLE-2025-H2` without administrative override | `CRITICAL` |
| **5** | **Untraceable Feedback** | Feedback | `FB-ANOMALY-UNTRACE-001` | Extreme feedback rating (1.00) without substantive commentary or evidence | `MEDIUM` |

---

## 12. Ground Truth Separation Methodology

To ensure uncompromised evaluation integrity:
1. Ground truth expected values are stored exclusively in external reference files:
   - `generated_data/starter/ground_truth.json` & `ground_truth.csv`
   - `generated_data/full/ground_truth.json` & `ground_truth.csv`
2. The Anomaly Detection Engine (`backend/app/services/anomaly_service.py`) **NEVER reads ground truth files**. It queries live PostgreSQL tables and evaluates structural heuristic invariants.
3. Ground-truth metadata is loaded post-scan to compute classification performance:

$$\text{Precision} = \frac{TP}{TP + FP} = \frac{5}{5 + 0} = 1.0000 \quad (100\%)$$

$$\text{Recall} = \frac{TP}{TP + FN} = \frac{5}{5 + 0} = 1.0000 \quad (100\%)$$

$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = 1.0000 \quad (100\%)$$

---

## 13. Independent Invariant Anomaly Detection

Trigger independent anomaly detection via the REST API or UI:

```bash
# Query open detected anomalies
curl -s http://localhost:8001/api/anomalies | jq .

# Trigger interactive remediation on a detected anomaly
curl -X POST http://localhost:8001/api/anomalies/ANO-000001/resolve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"resolution_action": "RECALCULATE", "resolution_notes": "Reconciled with ground truth baseline"}'
```

---

## 14. Comprehensive Data Exports Catalog (All 23 Relational Tables + SQL Seed)

YottaPerf provides dynamic, database-backed exports for all 23 normalized relational tables in both CSV and JSON formats, plus unified SQL seed dumps.

### Complete 23 Relational Tables Matrix:

| # | Database Table | Entity Type | Starter Count | Full Count | CSV Export File | JSON Export File |
|---|---|---|---|---|---|---|
| 1 | `employees` | Baseline Employees | 150 | 3,000 | `employees.csv` | `employees.json` |
| 2 | `user_accounts` | Security Accounts & Bcrypt Hashes | 150 | 3,000 | `user_accounts.csv` | `user_accounts.json` |
| 3 | `managers` | Baseline Active Managers | 25 | 500 | `managers.csv` | `managers.json` |
| 4 | `roles` | RBAC System Roles | 5 | 5 | `roles.csv` | `roles.json` |
| 5 | `employee_roles` | Employee-Role Bridge | 163 | 3,536 | `employee_roles.csv` | `employee_roles.json` |
| 6 | `review_cycles` | Appraisal Review Windows | 2 | 2 | `review_cycles.csv` | `review_cycles.json` |
| 7 | `competencies` | Capability Framework Frameworks | 10 | 12 | `competencies.csv` | `competencies.json` |
| 8 | `goals` | OKR Goals (Baseline + Injected Anomalies) | 510 | 10,040 | `goals.csv` | `goals.json` |
| 9 | `key_results` | Measurable KRs (Baseline + Anomalies) | 1,255 | 25,020 | `key_results.csv` | `key_results.json` |
| 10 | `goal_histories` | Immutable Goal Audit Snapshots | 1,000 | 20,000 | `goal_histories.csv` | `goal_histories.json` |
| 11 | `check_ins` | Periodic Progress Reports | 1,200 | 20,000 | `check_ins.csv` | `check_ins.json` |
| 12 | `evidences` | Cryptographically Linked Evidence Vault | 600 | 10,000 | `evidences.csv` | `evidences.json` |
| 13 | `feedbacks` | 360° Competency Feedback Entries | 906 | 18,036 | `feedbacks.csv` | `feedbacks.json` |
| 14 | `feedback_evidence` | Feedback-to-Evidence Bridge | 298 | 5,998 | `feedback_evidence.csv` | `feedback_evidence.json` |
| 15 | `reviews` | Calibration Performance Reviews | 300 | 6,000 | `reviews.csv` | `reviews.json` |
| 16 | `review_histories` | Review Stage State-Machine Transitions | 460 | 9,182 | `review_histories.csv` | `review_histories.json` |
| 17 | `review_permissions`| Authorized Reviewer Assignments | 298 | 5,998 | `review_permissions.csv` | `review_permissions.json` |
| 18 | `development_plans` | Individual Development Plans (IDPs) | 50 | 1,000 | `development_plans.csv` | `development_plans.json` |
| 19 | `development_activities`| IDP Courses, Milestones & Projects | 100 | 2,000 | `development_activities.csv`| `development_activities.json`|
| 20 | `development_plan_approvals`| Dual-Level Manager + HR Approvals | 49 | 999 | `development_plan_approvals.csv`| `development_plan_approvals.json`|
| 21 | `employee_manager_histories`| Historical Manager Transfers | 149 | 2,999 | `employee_manager_histories.csv`| `employee_manager_histories.json`|
| 22 | `anomalies` | Detected Exceptions Ledger | 25 | 100 | `anomalies.csv` | `anomalies.json` |
| 23 | `audit_events` | Tamper-Proof Administrative Ledger | 50 | 50 | `audit_events.csv` | `audit_events.json` |
| — | **Total Relational Records** | **23 Database Tables Scanned** | **7,755** | **147,477** | **Zero Integrity Violations** | **PASSED** |
| — | **SQL Database Seed** | Complete 3NF SQL Database Dump | All 23 Tables | All 23 Tables | `starter/seed.sql` | `full/seed.sql` |

### Authoritative Dataset Count Reconciliation & Baseline Breakdown:

| Metric Entity | Assignment Requirement | Starter Mode Breakdown | Full Mode Breakdown | Technical Reconciliation Note |
|---|---|---|---|---|
| **Employees** | 3,000 baseline in Full | **150** baseline | **3,000** baseline | 100% unique primary keys (`EMP-NNNNNN`). |
| **Managers** | 500 baseline in Full | **25** baseline | **500** baseline | 1:6 direct report ratio; zero circular hierarchy loops. |
| **Goals** | 10,000 baseline in Full | **500** baseline + **10** anomaly goals = **510 total** | **10,000** baseline + **40** anomaly goals = **10,040 total** | Baseline goals strictly meet requirements; anomaly goals (`GOAL-ANOMALY-*`) test detection engine. Past reports of 520 goals were un-reconciled drafts. |
| **Key Results** | Scaled proportional to goals | **1,250** baseline + **5** anomaly KRs = **1,255 total** | **25,000** baseline + **20** anomaly KRs = **25,020 total** | Anomaly KRs (`KR-ANOMALY-PROG-*`) test out-of-bounds formula progress validation. Past reports of 1,296 were draft miscounts. |
| **Check-Ins** | 20,000 baseline in Full | **1,200** baseline | **20,000** baseline | Exactly 20,000 check-ins generated and validated in full mode. |
| **Ground Truth** | Isolated offline artifact | **25** evaluation records | **100** evaluation records | Stored in `ground_truth.json` / `ground_truth.csv`. **Not** a 24th database table; sequestered from ordinary APIs. |

---

## 15. Deterministic Reproducibility Audit (Seed 20261022)

Running the generator twice with fixed seed `20261022` produces bit-for-bit identical row counts, derived progress figures, review scores, and SHA-256 checksums across all datasets:

| Dataset Export File | Starter Verified Rows | Full Verified Rows | Verified SHA-256 Checksum (Starter Seed: 20261022) |
|---|---|---|---|
| `csv/employees.csv` | 150 | 3,000 | `d277ca245aa54dfbda8d74d400a4f097be58e5dd8bd0cac27acc8477fc495400` |
| `csv/user_accounts.csv` | 150 | 3,000 | `754c4d78ab00106d0a62452d9a98493dd7c49346ef96a6633ee395b1b6ced5f5` |
| `csv/goals.csv` | 510 | 10,040 | `e3c69ba4975f008f8dd509f4649f573872d08de482d45bf29a17c73f4f7c3ae7` |
| `csv/key_results.csv` | 1,255 | 25,020 | `7a49de9009a18813d7b2e8f93771cb9f63eefc2d9a925d5e00d33a6a8858ce6c` |
| `csv/check_ins.csv` | 1,200 | 20,000 | `6be6fd2b3018272bf55c2ec9372765fe118e20b48e174950611a95b984ecf677` |
| `csv/evidences.csv` | 600 | 10,000 | `57126aad7a15a0bc90a8dd24d6b943a8bca3c592a9fb3639df03ea72948f96c3` |
| `csv/feedbacks.csv` | 906 | 18,036 | `7fd760bf395a04c0a9248b17c6fa5f1cd6bd9cca10de6d4d633b38e352c700e4` |
| `csv/reviews.csv` | 300 | 6,000 | `6ee34f7404689dedd52ef5dad79b26ec01bb58f7650ac52438d26921c321145a` |
| `csv/development_plans.csv` | 50 | 1,000 | `ce66857dc2ab10706eb1e3d63a54db3af9a4af59c62fd9fc2cbd06dbe97a9c4b` |
| `csv/anomalies.csv` | 25 | 100 | `257d6f97996ea31536d2b2d659a8d4307af7f5bc1d507c9b82ced28154faabc8` |
| `seed.sql` | — | — | `25face050366418e1191c4e767ad642842c9697f9703605c5cc050c379d9dd7d` |

---

## 16. Automated 15-Point Relational Validation Framework

The validation engine (`backend/validators/runner.py`) runs automated audit checks across all database records:

| Check | Validation Item | Description | Status |
|---|---|---|---|
| **A** | **Primary Key Uniqueness** | Ensures all entity IDs are unique and strictly formatted | `PASSED` |
| **B** | **Foreign Key Integrity** | Validates all parent-child references exist with 0 broken links | `PASSED` |
| **C** | **Allowed Enum Values** | Checks lifecycle stages, roles, priorities, directions | `PASSED` |
| **D** | **Date Monotonicity** | Validates `start_date` &le; `end_date` &le; `submission_deadline` | `PASSED` |
| **E** | **Goal & Key Result Consistency** | Reconciles child KR links and parent goal references | `PASSED` |
| **F** | **Review Cycle Consistency** | Validates cycle state rules and submission windows | `PASSED` |
| **G** | **Manager Hierarchy DAG** | DFS traversal verifies no circular reporting loops | `PASSED` |
| **H** | **Duplicate Record Detection** | Scans for semantic duplicate tuples | `PASSED` |
| **I** | **Progress Calculation Correctness** | Recalculates KR formulas against stored readings | `PASSED` |
| **J** | **Weighted Score Reconciliation** | Verifies goal progress = &sum;(KR progress &times; KR weight) | `PASSED` |
| **K** | **Review Lifecycle State Machine**| Validates valid transition paths | `PASSED` |
| **L** | **Role & Permission Rules** | Enforces RBAC constraints and self-approval bans | `PASSED` |
| **M** | **Audit History Completeness** | Validates audit trail for all modifications | `PASSED` |
| **N** | **Development Plan Approvals** | Verifies manager and HR dual-approval rules | `PASSED` |
| **O** | **Anomaly & Ground-Truth Consistency**| Verifies 100% precision and recall of injected anomalies | `PASSED` |

```bash
# Execute 15-Point Validation on Starter Dataset (7,755 records)
docker compose exec backend python -m backend.validators.runner --dataset-dir generated_data/starter

# Execute 15-Point Validation on Full Dataset (147,477 records)
docker compose exec backend python -m backend.validators.runner --dataset-dir generated_data/full
```

---

## 17. Project Directory Structure

```
YottaPerf/
├── backend/                         # Backend Application
│   ├── app/
│   │   ├── api/                     # 12 Modular REST Routers
│   │   │   ├── admin.py             # Dataset generation & validation endpoints
│   │   │   ├── anomalies.py         # Anomaly detection & interactive remediation
│   │   │   ├── auth.py              # JWT authentication & session inspection
│   │   │   ├── checkins.py          # Periodic check-in operations
│   │   │   ├── competencies.py      # Competency catalog endpoints
│   │   │   ├── dashboard.py         # KPI & telemetry aggregations
│   │   │   ├── development.py       # Individual Development Plans (IDPs)
│   │   │   ├── employees.py         # Employee directory & 360 profile drawer
│   │   │   ├── feedback.py          # 360° feedback submission & conflict handling
│   │   │   ├── goals.py             # OKR goals, Key Results, and progress derivation
│   │   │   ├── organization.py      # Org hierarchy & DFS transfer operations
│   │   │   ├── reviews.py           # Review calibration scoring & stage transitions
│   │   │   └── main.py              # FastAPI app initialization & CORS middleware
│   │   ├── core/                    # App configuration, database connection, JWT security
│   │   ├── models/                  # 23 SQLAlchemy 2.0 ORM models
│   │   ├── permissions/             # RBAC role guards & permission dependencies
│   │   ├── schemas/                 # Pydantic v2 validation schemas
│   │   └── services/                # Business logic services (goals, org, reviews, etc.)
│   ├── generator/                   # Deterministic synthetic data generator engine
│   ├── validators/                  # 15-point automated validation engine
│   ├── tests/                       # 27 Automated Pytest integration & security tests
│   ├── migrations/                  # Alembic database migrations
│   ├── Dockerfile                   # Python 3.12 Backend Dockerfile
│   └── requirements.txt             # Backend Python dependencies
├── frontend/                        # Next.js 14 Frontend Application
│   ├── app/                         # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/                  # Reusable UI components & 13 distinct views
│   │   ├── Navbar.tsx               # Header with Live RBAC Persona Switcher
│   │   ├── Sidebar.tsx              # Navigation & Active Session Persona Card
│   │   └── views/                   # 13 Dedicated Views (Dashboard, OKRs, Org, Anomalies, etc.)
│   ├── services/                    # Typed Axios API Client with JWT interception
│   ├── types/                       # TypeScript interfaces matching backend models
│   ├── Dockerfile                   # Multi-stage production build Dockerfile
│   └── package.json                 # Next.js 14, React 19, Tailwind CSS dependencies
├── database/
│   ├── schema.sql                   # PostgreSQL 3NF DDL schema
│   └── seed/                        # SQL starter seed script
├── generated_data/
│   ├── starter/                     # Starter dataset (CSV, JSON, SQL seed, ground_truth)
│   └── full/                        # Full dataset (147k records, 3k employees, 10k goals)
├── docs/                            # Comprehensive documentation suite
│   ├── final_submission_audit.md    # Formal submission audit report & evidence
│   ├── architecture.md              # System architecture specification
│   ├── business_rules.md            # Mathematical formulas & business rules
│   ├── database_relationships.md    # ERD and entity relationship models
│   ├── data_dictionary.md           # 23-table data dictionary
│   └── validation_report.md         # 15-point validation report
├── ARCHITECTURE.md                  # Root architectural specification link
├── DESIGN_DECISIONS.md              # Engineering trade-offs and rationale
├── TESTING.md                       # Test catalog, invariants, and execution logs
├── DEMO_GUIDE.md                    # 5–10 minute evaluator walkthrough script
├── docker-compose.yml               # Multi-container orchestration (DB, Backend, Frontend)
├── .env.example                     # Environment configuration template
├── pytest.ini                       # Pytest test configuration
├── .gitignore                       # Git ignore rules
└── README.md                        # Master project guide
```

---

## 18. Prerequisites & Environment Configuration

### Prerequisites:
- **Docker & Docker Compose:** Ensure Docker Desktop (Windows/macOS) or Docker Engine (Linux) is running.
- **Zero Host Dependencies:** Python, Node.js, and PostgreSQL are not required on your host machine.

### Environment Configuration:
YottaPerf is pre-configured for zero-configuration evaluation. Safe, production-grade default environment values are embedded directly inside `docker-compose.yml`:

```env
POSTGRES_USER=yotta_user
POSTGRES_PASSWORD=yotta_password
POSTGRES_DB=yottaperf_db
DATABASE_URL=postgresql://yotta_user:yotta_password@postgres:5432/yottaperf_db
PORT=8001
SECRET_KEY=yottaperf-super-secure-jwt-secret-key-change-in-production
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

*(Optional Developer Customization)*: To override ports or credentials, copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## 19. Docker Operations & Developer Setup (Optional)

### Standard Docker Operations:
```bash
# Launch platform in detached mode
docker compose up --build -d

# Inspect container health probes and running status
docker compose ps

# View live aggregate logs
docker compose logs -f

# View logs for a specific service
docker compose logs backend -f
docker compose logs frontend -f
docker compose logs postgres -f

# Stop running containers
docker compose down

# Stop containers and purge PostgreSQL volume for a complete fresh re-initialization
docker compose down -v
```

---

## 20. Running Automated Tests & Verified Pytest Log

```bash
docker compose exec backend pytest backend/tests/ -v
```

### Verified Pytest Log Output (27 Tests Passed):
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

## 21. Security, RBAC & Verified Personas Matrix

> [!NOTE]
> **Demonstration-Only Credentials Notice:** The credentials below (`Password123!`) are provisioned exclusively for local offline evaluator demonstration and automated testing in development environments. In production mode, passwords must be securely hashed using per-user cryptographic salts (bcrypt/argon2), secrets managed through zero-trust secret vaults (e.g., HashiCorp Vault / AWS Secrets Manager), and hardcoded default secrets are strictly rejected at startup.

All seeded user accounts share the initial demonstration password: **`Password123!`**. Evaluators can switch between personas in real time using the **Role Persona Switcher** in the top-right corner of the Navbar:

| Persona | DB Username | Position / Department | Granted Roles | Key Authority & Permissions |
|---|---|---|---|---|
| **Eleanor Vance** | `eleanor.vance` | Chief Executive Officer (Executive) | `ADMIN`, `MANAGER` | Full administrative control, closed-cycle overrides, unmasked ground-truth anomaly labels |
| **Melissa Williams** | `melissa.williams` | VP Product & HR Partner (Product) | `HR_PARTNER`, `MANAGER` | Review calibration approvals, cycle operations, dual IDP approvals, talent analytics |
| **Erin Riley** | `erin.riley` | VP Engineering (Engineering) | `MANAGER` | Direct report OKR cascading, check-in reviews, manager ratings, IDP approvals |
| **Anthony Fletcher** | `anthony.fletcher32` | DevOps & IT Ops Lead (Engineering) | `IT_OPS`, `EMPLOYEE` | Synthetic generator controls, automated validation engine, audit trail inspection |
| **Victoria Mendoza** | `victoria.mendoza26` | Senior Software Engineer (Engineering) | `EMPLOYEE` | Self-goal management, check-in updates, self-evaluations. Anomaly ground truth is strictly masked |

---

## 22. Expected Outputs & Verification Commands

### 1. Verify Entity Counts in PostgreSQL
```bash
docker compose exec postgres psql -U yotta_user -d yottaperf_db -c "
SELECT 'employees' AS table_name, count(*) FROM employees
UNION ALL SELECT 'goals', count(*) FROM goals
UNION ALL SELECT 'key_results', count(*) FROM key_results
UNION ALL SELECT 'check_ins', count(*) FROM check_ins
UNION ALL SELECT 'feedbacks', count(*) FROM feedbacks
UNION ALL SELECT 'reviews', count(*) FROM reviews
UNION ALL SELECT 'development_plans', count(*) FROM development_plans
UNION ALL SELECT 'anomalies', count(*) FROM anomalies;
"
```

### 2. Verify Anomaly Precision and Recall (100% / 100%)
```bash
curl -s http://localhost:8001/api/anomalies | jq '{total_anomalies: length, critical_count: ([.[] | select(.severity == "CRITICAL")] | length)}'
```

### 3. Verify Foreign Key Integrity (Must Return 0)
```bash
docker compose exec postgres psql -U yotta_user -d yottaperf_db -c "
SELECT count(*) AS broken_goals FROM goals g LEFT JOIN employees e ON g.employee_id = e.employee_id WHERE e.employee_id IS NULL;
"
```

---

## 23. Troubleshooting Guide

### 1. Docker Daemon Not Running
- **Symptom:** `Cannot connect to the Docker daemon at unix:///var/run/docker.sock` or `docker: command not found`.
- **Resolution:** Open Docker Desktop and confirm the whale icon indicates "Engine running". On Linux, run `sudo systemctl start docker`.

### 2. Port Collisions (Port 3002, 8001, or 5434 already in use)
- **Symptom:** `Bind for 0.0.0.0:8001 failed: port is already allocated`.
- **Resolution:** Change the host port mapping in `docker-compose.yml` (e.g. `"8002:8001"` or `"3003:3000"`).

### 3. Resetting and Cold Re-generating from Scratch
- **Symptom:** Need to purge database volumes and test complete fresh initialization.
- **Resolution:**
  ```bash
  docker compose down -v
  docker compose up --build -d
  ```

---

## 24. Limitations, Assumptions & Public Submission Links

- **Synthetic Data Realism:** All employee names, emails, and job titles are generated deterministically using Faker and NumPy distributions with seed `20261022`; they contain zero personally identifiable information (PII).
- **Relational Currency & Measurements:** All metric units (currency, latency, percentages, counts) are simulated for enterprise benchmarking.
- **Single Universal Evaluator Command:** `docker compose up --build -d`.
- **Public Repository:** [https://github.com/usharani222/YottaPerf](https://github.com/usharani222/YottaPerf)
- **Formal Verification Audit:** [docs/final_submission_audit.md](docs/final_submission_audit.md)
