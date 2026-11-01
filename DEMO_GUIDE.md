# YottaPerf — Evaluator Demonstration Guide & Technical Q&A

This guide provides an evaluator or technical interviewer with a 5–10 minute step-by-step demonstration workflow to verify all key capabilities of the **YottaPerf** platform.

---

## ⚡ Quick Verification Checklist (Under 2 Minutes)

1. **Verify Services Running:**
   ```bash
   docker compose ps
   ```
   *Expected:* `yottaperf-db` (healthy, port 5434), `yottaperf-backend` (healthy, port 8001), and `yottaperf-frontend` (running, port 3002).

2. **Verify Backend Health Probe:**
   ```bash
   curl -s http://localhost:8001/health | jq .
   ```
   *Expected:* `{"status": "healthy", "database": "connected"}`.

3. **Verify Automated Tests:**
   ```bash
   docker compose exec backend pytest backend/tests/ -v
   ```
   *Expected:* `27 passed in < 1.0s`.

4. **Verify 15-Point Automated Dataset Validation:**
   ```bash
   docker compose exec backend python -m backend.validators.runner --dataset-dir generated_data/starter
   ```
   *Expected:* `overall_validation_status: PASSED (7,755 records verified)`.

---

## 🎯 Step-by-Step Evaluator Walkthrough (5–10 Minutes)

### Step 1: Open the Aurora Enterprise Command Center
- Open your browser to **`http://localhost:3002/`**.
- Notice the **Aurora Glassmorphic Theme**: Dark slate palette (`#030712`), curated emerald/cyan gradient glows, and typography.
- Inspect the **KPI Cards**: Total Employees (150 in starter), Total Managers (25), Total Goals (510), Active Review Cycles, Average Goal Progress (mathematically weighted), and Open Anomalies.
- Review the **Operational Risk & Velocity Indicators**: Goals at Risk, Overdue Goals, Overdue Check-Ins, Review Completion percentage, and Critical Anomalies.

### Step 2: Test Live Persona & Role Switching (RBAC)
- Click the **Role Switcher** capsule in the top-right corner of the Navbar.
- Select **`Melissa Williams`** (VP Product & HR Partner — `HR_PARTNER, MANAGER`).
  - *Observation:* The Navbar and Sidebar active session cards update instantly. Review calibration controls become active.
- Select **`Victoria Mendoza`** (Senior Software Engineer — `EMPLOYEE`).
  - *Observation:* The session switches to employee context.
- Navigate to the **Anomaly Defense Center** tab in the sidebar.
  - *RBAC Proof:* Notice that ground-truth labels in the table display as **`[Lock] Restricted Role`** because Victoria lacks `ADMIN` privileges.
- Switch back to **`Eleanor Vance`** (`ADMIN, MANAGER`).
  - *Observation:* Full administrative access is restored, and ground-truth labels are unmasked.

### Step 3: Inspect 360° Employee Directory & Performance Profile
- Click **Employee Directory** in the sidebar.
- Use the search bar or department filter (e.g., *Engineering*).
- Click on an employee row (e.g. *Eleanor Vance* or *Melissa Williams*).
- A slide-over **Performance Profile Drawer** appears displaying:
  - Org position & reporting manager
  - Direct reports count
  - Active OKRs and weighted progress bars
  - Historical check-in cadence with linked evidence
  - 360° feedback ratings across competencies
  - Calibration review score & Individual Development Plan (IDP)

### Step 4: Explore Organization Graph & Hierarchy
- Click **Org Graph & Hierarchy** in the sidebar.
- Inspect the interactive DAG visualization showing non-circular reporting structures.
- Click **Transfer Manager** to simulate a reporting transfer. Notice that attempting to assign an employee to their own direct report triggers DFS cycle detection and rejects the update with a clear diagnostic message.

### Step 5: Goals & OKRs Evidence Timeline
- Click **Goals & OKRs** in the sidebar.
- Expand a goal card to view individual Key Results.
- Notice both **Increasing Metrics** (e.g., *Feature Adoption Rate from 10% to 80%*) and **Decreasing Metrics** (e.g., *P99 Latency from 450ms to 80ms*).
- Click **View Evidence Timeline** on any check-in to see verified links (`CODE_PR`, `DOCUMENT`, `DASHBOARD`).

### Step 6: Exception & Anomaly Resolution Center
- Click **Anomaly Defense Center** in the sidebar.
- Inspect the 5 injected negative anomaly scenarios:
  1. `GOAL_OWNER_MISMATCH`
  2. `INVALID_PROGRESS`
  3. `INVALID_REVIEWER`
  4. `CLOSED_CYCLE_MODIFICATION`
  5. `UNTRACEABLE_FEEDBACK`
- Click **Remediate** on any anomaly row:
  - An interactive modal opens displaying diagnostic details and recommended resolution actions.
  - Enter resolution notes and click **Confirm Remediation**.
  - Notice the status immediately changes to **`RESOLVED`**, and an immutable audit entry is committed.

---

## 💡 Interviewer Technical Q&A Talking Points

### Q1: How does YottaPerf guarantee that progress is strictly derived rather than self-reported?
> **Answer:** YottaPerf never allows clients to directly overwrite overall goal progress. Instead, employees update current readings on individual Key Results. The system calculates each KR's progress based on metric direction (increasing vs decreasing) with division-by-zero safeguards, and computes goal progress as the strict weighted sum ($\sum w_i \times p_i$) of all child KRs.

### Q2: How does the system prevent circular reporting loops in the org hierarchy?
> **Answer:** When a manager transfer is requested, the service performs an in-memory Depth-First Search (DFS) traversal starting from the proposed manager's lineage. If the employee being transferred appears in the ancestry tree of the target manager, a cycle is detected, and the transaction is aborted with `HTTP 400 Bad Request`.

### Q3: How is ground-truth separation maintained during anomaly detection?
> **Answer:** Ground-truth files (`ground_truth.json` / `ground_truth.csv`) are stored externally and are never read by the anomaly detection service (`anomaly_service.py`). The detector queries solely against live PostgreSQL tables and evaluates invariant rules. Ground truth is loaded only post-scan by the verification evaluator to compute classification metrics (100% precision & recall).

### Q4: How is closed-cycle immutability enforced?
> **Answer:** Review cycles maintain lifecycle states (`DRAFT`, `OPEN`, `IN_REVIEW`, `CLOSED`, `ARCHIVED`). Any API mutation targeting a closed cycle is blocked by FastAPI security guards. If an administrative override is performed, the system captures pre- and post-modification state snapshots and records an immutable audit record in the `audit_events` table.
