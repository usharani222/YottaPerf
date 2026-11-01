import os
import csv
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any


def compute_file_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def export_dataset(
    tables_data: Dict[str, List[Dict[str, Any]]],
    output_dir: str,
    mode: str,
    seed: int
) -> Dict[str, Any]:
    """
    Exports all relational dataset tables to:
    - CSV format in /csv
    - JSON format in /json
    - SQL INSERT statements in seed.sql
    - source manifest in manifest.json
    """
    csv_dir = os.path.join(output_dir, "csv")
    json_dir = os.path.join(output_dir, "json")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    row_counts = {}
    file_hashes = {}

    # 1. Export CSV and JSON
    for table_name, rows in tables_data.items():
        row_counts[table_name] = len(rows)
        
        # JSON
        json_file = os.path.join(json_dir, f"{table_name}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, default=str)
        file_hashes[f"json/{table_name}.json"] = compute_file_sha256(json_file)

        # CSV
        csv_file = os.path.join(csv_dir, f"{table_name}.csv")
        if rows:
            fieldnames = list(rows[0].keys())
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k) for k in fieldnames})
        else:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                pass
        file_hashes[f"csv/{table_name}.csv"] = compute_file_sha256(csv_file)

    # 2. Export SQL Seed Script
    sql_file = os.path.join(output_dir, "seed.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("-- YottaPerf Generated Deterministic SQL Seed Dataset\n")
        f.write(f"-- Mode: {mode}, Seed: {seed}, Reference Date: 2026-06-30\n\n")
        
        # Write in dependency order
        insertion_order = [
            "roles", "competencies", "review_cycles", "employees", "user_accounts",
            "employee_roles", "managers", "employee_manager_histories", "goals",
            "key_results", "goal_histories", "check_ins", "evidences", "feedbacks",
            "feedback_evidence", "review_permissions", "reviews", "review_histories",
            "development_plans", "development_activities", "development_plan_approvals",
            "anomalies", "audit_events"
        ]
        
        for tbl in insertion_order:
            rows = tables_data.get(tbl, [])
            if not rows:
                continue
            cols = list(rows[0].keys())
            cols_str = ", ".join(cols)
            f.write(f"-- Table: {tbl} ({len(rows)} records)\n")
            for r in rows:
                vals = []
                for c in cols:
                    val = r.get(c)
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, bool):
                        vals.append("TRUE" if val else "FALSE")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    elif isinstance(val, dict):
                        vals.append(f"'{json.dumps(val)}'::jsonb")
                    else:
                        escaped = str(val).replace("'", "''")
                        vals.append(f"'{escaped}'")
                f.write(f"INSERT INTO {tbl} ({cols_str}) VALUES ({', '.join(vals)}) ON CONFLICT DO NOTHING;\n")
            f.write("\n")

    file_hashes["seed.sql"] = compute_file_sha256(sql_file)

    # Overall dataset composite hash
    combined_hashes = "".join(f"{k}:{v}\n" for k, v in sorted(file_hashes.items()))
    dataset_checksum = hashlib.sha256(combined_hashes.encode("utf-8")).hexdigest()

    # 3. Create Manifest
    manifest = {
        "dataset_name": f"YottaPerf Synthetic Dataset ({mode.upper()})",
        "generation_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator_version": "1.0.0",
        "random_seed": seed,
        "generation_mode": mode,
        "entity_row_counts": row_counts,
        "dataset_checksum": dataset_checksum,
        "file_checksums": file_hashes,
        "synthetic_data_declaration": (
            "This entire dataset is purely synthetic and deterministically generated using "
            "Python, Faker, and NumPy with fixed seed 20261022. It contains no personally identifiable "
            "information (PII) or real confidential organizational data."
        ),
        "external_data_provenance": "No external proprietary or confidential employee data used."
    }

    manifest_file = os.path.join(output_dir, "manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest
