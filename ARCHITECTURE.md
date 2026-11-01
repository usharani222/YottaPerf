# YottaPerf — Architecture Overview

*For the complete detailed architecture specification, see [docs/architecture.md](docs/architecture.md).*

---

## High-Level System Architecture

YottaPerf is organized into four modular layers:
1. **Presentation Layer:** Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide Icons, and Recharts telemetry dashboards with Aurora glassmorphic theme.
2. **Application & API Gateway:** FastAPI async REST endpoints, Pydantic v2 schemas, and JWT Role-Based Access Control (RBAC) guards.
3. **Core Business Engines:**
   - **Org Hierarchy Engine:** Depth-First Search (DFS) directed acyclic graph (DAG) cycle prevention.
   - **OKR Derivation Engine:** Strictly computed progress for increasing & decreasing metrics.
   - **Review Calibration Engine:** Transparent 50/30/20 composite scoring model.
   - **Anomaly Defense Engine:** Independent invariant rules scanner.
   - **Audit Ledger Engine:** Pre/post state serialization for closed-cycle overrides.
4. **Data & Storage Layer:** PostgreSQL 16 3NF normalized schema across 23 tables, managed by SQLAlchemy 2.0 ORM and Alembic migrations.

---

## 3NF Relational Architecture (23 Tables)

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

Refer to:
- [Database Relationships & ERD](docs/database_relationships.md)
- [Data Dictionary (23 Tables)](docs/data_dictionary.md)
- [Business Rules & Formulas](docs/business_rules.md)
- [Design Decisions](DESIGN_DECISIONS.md)
