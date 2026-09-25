"""
Unit tests for 14-Section Report Builder and Journey Mapper.
Phase 10 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from pathlib import Path
from src.collectors.file_mock_collector import FileMockCollector
from src.processors.extractor import EvidenceExtractor
from src.processors.classifier import TaxonomyClassifier
from src.processors.clusterer import ProblemClusterer
from src.processors.metric_decomposer import BusinessMetricDecomposer
from src.processors.hypothesis_generator import HypothesisGenerator
from src.generators.report_builder import ReportBuilder


def build_full_test_pipeline_artifacts():
    mock_file = Path("data/raw_inputs/sample_evidence.json")
    collector = FileMockCollector(filepath=mock_file)
    raw_items = collector.collect(["test"])

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

    return classified_records, clusters, matrix, funnel, hypotheses


def test_report_builder_14_sections_and_closing(tmp_path):
    records, clusters, matrix, funnel, hypotheses = build_full_test_pipeline_artifacts()

    builder = ReportBuilder()
    output_file = tmp_path / "research-findings.md"
    report_text = builder.build_report(
        records=records,
        clusters=clusters,
        matrix=matrix,
        funnel=funnel,
        hypotheses=hypotheses,
        output_filepath=output_file,
    )

    assert output_file.exists()
    assert len(report_text) > 1000

    # Verify all 14 required section headers exist in exact numerical sequence
    expected_sections = [
        "## Section 1: Executive Summary",
        "## Section 2: Source Landscape",
        "## Section 3: Retrieval Problem Taxonomy",
        "## Section 4: Evidence Table (Complete 19-Field Database)",
        "## Section 5: Memory Taxonomy Analysis",
        "## Section 6: Representative Retrieval Journeys",
        "## Section 7: Business Metric Funnel Decomposition",
        "## Section 8: Opportunity Areas (Comparison Matrix)",
        "## Section 9: Evidence-Backed User Segments",
        "## Section 10: AI Opportunity Map",
        "## Section 11: Research Gaps & Limitations",
        "## Section 12: Falsifiable User Interview Hypotheses",
        "## Section 13: Recommended Next-Phase User Research Design",
        "## Section 14: Product Manager Takeaways",
        "## WHAT I SHOULD DO NEXT",
    ]

    for section_hdr in expected_sections:
        assert section_hdr in report_text

    # Verify Section 4 contains 19-field table headers
    assert "Source Platform" in report_text or "Platform" in report_text
    assert "Verbatim User Quote" in report_text
    assert "Stage" in report_text
    assert "Category" in report_text

    # Verify Section 6 contains 5 to 10 journey flows
    assert "JOURNEY-01" in report_text
    assert "JOURNEY-05" in report_text

    # Verify Section 12 contains hypotheses table with falsification conditions
    assert "HYP-001" in report_text
    assert "Falsification Condition" in report_text
