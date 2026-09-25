"""
Unit tests for Research Quality Rules QualityChecker Suite.
Phase 12 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
import json
from pathlib import Path

from src.qa.quality_checker import QualityChecker, QAReport
from src.collectors.base import RawEvidenceItem
from src.processors.extractor import EvidenceExtractor
from src.processors.classifier import TaxonomyClassifier
from src.processors.clusterer import ProblemClusterer
from src.processors.metric_decomposer import BusinessMetricDecomposer
from src.processors.hypothesis_generator import HypothesisGenerator
from src.generators.report_builder import ReportBuilder


def setup_valid_test_artifacts(tmp_path):
    mock_file = Path("data/raw_inputs/sample_evidence.json")
    with open(mock_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    raw_items = [RawEvidenceItem.model_validate(d) for d in raw_data]

    extractor = EvidenceExtractor()
    records = extractor.extract_batch(raw_items)

    classifier = TaxonomyClassifier()
    classified_records = classifier.classify_batch(records)

    clusterer = ProblemClusterer(high_freq_threshold=2, med_freq_threshold=1)
    clusters = clusterer.cluster_records(classified_records)
    matrix = clusterer.build_opportunity_matrix(clusters)

    decomposer = BusinessMetricDecomposer()
    funnel = decomposer.decompose(classified_records)

    hypo_gen = HypothesisGenerator()
    hypotheses = hypo_gen.generate_hypotheses(clusters, funnel)

    builder = ReportBuilder()
    report_file = tmp_path / "research-findings.md"
    builder.build_report(
        records=classified_records,
        clusters=clusters,
        matrix=matrix,
        funnel=funnel,
        hypotheses=hypotheses,
        output_filepath=report_file,
    )

    json_db_file = tmp_path / "evidence_database.json"
    data = [r.model_dump(mode="json") for r in classified_records]
    with open(json_db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return report_file, json_db_file, raw_items


def test_qa_checker_valid_artifacts(tmp_path):
    report_file, json_db_file, raw_items = setup_valid_test_artifacts(tmp_path)

    checker = QualityChecker()
    qa_report = checker.validate(
        report_path=report_file,
        json_db_path=json_db_file,
        raw_items=raw_items,
    )

    assert isinstance(qa_report, QAReport)
    assert qa_report.status == "PASS"
    assert qa_report.zero_fabrication_pass is True
    assert qa_report.citation_resolution_pass is True
    assert qa_report.claim_tagging_pass is True
    assert qa_report.confidence_labeling_pass is True
    assert qa_report.schema_completeness_pass is True
    assert qa_report.report_structure_pass is True
    assert len(qa_report.violations) == 0


def test_qa_checker_detects_violations(tmp_path):
    report_file, json_db_file, raw_items = setup_valid_test_artifacts(tmp_path)

    # Invalidate citation URL in evidence database
    with open(json_db_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[0]["source_url"] = "invalid_url_without_http"
    with open(json_db_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    checker = QualityChecker()
    qa_report = checker.validate(
        report_path=report_file,
        json_db_path=json_db_file,
        raw_items=raw_items,
    )

    assert qa_report.status == "FAIL"
    assert qa_report.citation_resolution_pass is False
    assert len(qa_report.violations) >= 1
    assert qa_report.violations[0].rule_id == "RULE-02"


def test_qa_report_export(tmp_path):
    report_file, json_db_file, raw_items = setup_valid_test_artifacts(tmp_path)
    checker = QualityChecker()
    qa_report = checker.validate(report_file, json_db_file, raw_items)

    output_json = tmp_path / "qa_report.json"
    exported = checker.export_qa_report(qa_report, output_json)
    assert exported.exists()

    data = json.loads(exported.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
