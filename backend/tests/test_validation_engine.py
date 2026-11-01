import os
import pytest
from backend.generator.config import get_generator_config
from backend.generator.runner import generate_all_data
from backend.generator.exporter import export_dataset
from backend.validators.engine import ValidationEngine


def test_17_18_19_validation_engine_integrity_and_anomalies():
    """TEST 17, 18, & 19: Foreign key validation, anomaly detection, and ground truth consistency."""
    config = get_generator_config(mode="starter", seed=20261022)
    tables_data, ground_truth = generate_all_data(config)

    engine = ValidationEngine()
    report = engine.validate_dataset(tables_data, ground_truth)

    # TEST 17: Foreign key validation passes for valid baseline records
    assert report.foreign_key_violations == 0, f"FK violations: {report.details}"
    assert report.primary_key_violations == 0
    assert report.circular_hierarchy_violations == 0

    # TEST 18: Injected anomalies are detected and categorized
    assert report.detected_anomalies >= 25
    ano_types = {a["issue_type"] for a in tables_data["anomalies"]}
    required_types = {
        "GOAL_OWNER_MISMATCH",
        "INVALID_PROGRESS",
        "INVALID_REVIEWER",
        "CLOSED_CYCLE_MODIFICATION",
        "UNTRACEABLE_FEEDBACK"
    }
    assert required_types.issubset(ano_types), f"Missing required anomalies: {required_types - ano_types}"

    # TEST 19: Ground truth consistency (every anomaly maps 1-to-1 to a ground truth record)
    assert report.ground_truth_mismatches == 0
    assert len(ground_truth) == len(tables_data["anomalies"])
    assert report.overall_status == "PASSED"


def test_20_fixed_seed_reproducibility(tmp_path):
    """TEST 20: Fixed-seed reproducibility produces identical row counts, IDs, field values, and checksums."""
    dir1 = str(tmp_path / "run1")
    dir2 = str(tmp_path / "run2")

    config = get_generator_config(mode="starter", seed=20261022)

    # First run
    tables1, gt1 = generate_all_data(config)
    manifest1 = export_dataset(tables1, dir1, config.mode, config.seed)

    # Second run with identical seed
    tables2, gt2 = generate_all_data(config)
    manifest2 = export_dataset(tables2, dir2, config.mode, config.seed)

    # Checksums must be bit-for-bit identical
    assert manifest1["dataset_checksum"] == manifest2["dataset_checksum"]
    assert manifest1["entity_row_counts"] == manifest2["entity_row_counts"]
    assert len(gt1) == len(gt2)
    for i in range(len(gt1)):
        assert gt1[i] == gt2[i]
