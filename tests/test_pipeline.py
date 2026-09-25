"""
Unit & Integration tests for DiscoveryPipeline End-to-End Orchestrator.
Phase 11 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from pathlib import Path
from src.config import load_config
from src.pipeline import DiscoveryPipeline


def test_discovery_pipeline_sample_run(tmp_path):
    config = load_config(
        config_path="config/default_config.yaml",
        mode_override="sample",
        output_dir_override=str(tmp_path / "output")
    )

    pipeline = DiscoveryPipeline(config)
    result = pipeline.run()

    assert result["status"] == "SUCCESS"
    assert result["raw_items_count"] >= 5
    assert result["unique_records_count"] >= 5
    assert result["problem_clusters_count"] >= 3
    assert 8 <= result["hypotheses_count"] <= 12

    report_file = Path(result["report_path"])
    json_db_file = Path(result["database_json_path"])
    sqlite_db_file = Path(result["sqlite_db_path"])

    assert report_file.exists()
    assert json_db_file.exists()
    assert sqlite_db_file.exists()

    report_text = report_file.read_text(encoding="utf-8")
    assert "Section 1: Executive Summary" in report_text
    assert "Section 4: Evidence Table" in report_text
    assert "WHAT I SHOULD DO NEXT" in report_text
