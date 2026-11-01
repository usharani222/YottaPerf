import csv
import json
import os
from typing import List, Dict, Any, Tuple


def export_ground_truth(
    ground_truth_records: List[Dict[str, Any]],
    output_dir: str
) -> Tuple[str, str]:
    """
    Exports ground truth records strictly isolated to ground_truth.csv and ground_truth.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "ground_truth.csv")
    json_path = os.path.join(output_dir, "ground_truth.json")

    # CSV Export
    fieldnames = ["record_id", "entity_type", "issue_type", "expected_label", "expected_decision", "explanation"]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in ground_truth_records:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    # JSON Export (deterministic indent and sorting)
    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(ground_truth_records, f, indent=2, sort_keys=True)

    return csv_path, json_path
