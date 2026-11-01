# Automated Validation Report: FULL

## 1. Executive Summary

| Metric | Result | Status |
|---|---|---|
| **Overall Validation Status** | **PASSED** | ✅ PASS |
| Total Records Validated | 147,477 | Scanned across 23 tables |
| Primary Key Violations | 0 | ✅ 0 Violations |
| Foreign Key Integrity Violations | 0 | ✅ 0 Violations |
| Invalid Date Sequences | 0 | ✅ 0 Violations |
| Circular Hierarchy Violations | 0 | ✅ 0 Cycles |
| Duplicate Composite Records | 0 | ✅ 0 Duplicates |
| Invalid Enum Values | 0 | ✅ 0 Violations |
| Invalid Progress Calculations | 0 | ✅ 0 Discrepancies |
| Weighted Score Mismatches | 0 | ✅ 0 Discrepancies |
| Injected / Detected Anomalies | 120 | Formatted & registered |
| Ground Truth Mismatches | 0 | ✅ 100% Match |

## 2. Validation Checks Detail

- **A. Primary Key Uniqueness**: Verified unique constraint across all 23 entities.
- **B. Foreign Key Integrity**: Verified parent references across reporting managers, cycle IDs, goal owners, and review assignments.
- **C. Allowed Enum Values**: Verified strict domain sets for stages, categories, and metric directions.
- **D. Date Sequence Ordering**: Verified start dates precede due dates and cycle closing dates.
- **E. Hierarchy Consistency**: Cycle-detection algorithm confirmed 0 circular reporting loops.
- **F. Mathematical Integrity**: Verified Key Result formula recalculation and weighted review score reconciliation.
- **G. Ground Truth Consistency**: Verified that all injected anomalies match the ground truth registry 1-to-1 without contaminating ordinary application records.

```json
{
  "total_records_validated": 147477,
  "primary_key_violations": 0,
  "foreign_key_violations": 0,
  "invalid_date_sequences": 0,
  "invalid_enum_values": 0,
  "invalid_progress_calculations": 0,
  "weighted_score_mismatches": 0,
  "invalid_lifecycle_transitions": 0,
  "duplicate_records": 0,
  "circular_hierarchy_violations": 0,
  "detected_anomalies": 120,
  "ground_truth_mismatches": 0,
  "overall_validation_status": "PASSED",
  "details_count": 0
}
```
