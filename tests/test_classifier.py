"""
Unit tests for Taxonomy Classification Engine.
Phase 6 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from pathlib import Path
from src.collectors.file_mock_collector import FileMockCollector
from src.processors.extractor import EvidenceExtractor
from src.processors.classifier import TaxonomyClassifier
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import (
    FailureStage,
    FailureCategory,
    MemoryClueType,
    EvidenceStrength,
    ClaimTag,
)


def create_gold_standard_benchmark_records() -> list[EvidenceRecord]:
    """
    Creates 10 gold-standard benchmark records representing distinct failure stages and categories.
    """
    extractor = EvidenceExtractor()
    mock_file = Path("data/raw_inputs/sample_evidence.json")
    collector = FileMockCollector(filepath=mock_file)
    raw_items = collector.collect(queries=["test"])
    records = extractor.extract_batch(raw_items)

    # Add additional synthetic gold standard records to reach 10 benchmark items
    extra_1 = EvidenceRecord(
        evidence_id="EV-GOLD-007",
        source_platform="Reddit",
        source_url="https://reddit.com/r/googlephotos/comments/gold7",
        user_quote="I know what I want to search for, but I just can't remember the exact date or place name.",
        user_intent="Express vague memory",
        failure_stage=FailureStage.STAGE_1,
        failure_category=FailureCategory.A,
        evidence_strength=EvidenceStrength.MEDIUM,
    )
    extra_2 = EvidenceRecord(
        evidence_id="EV-GOLD-008",
        source_platform="Google Play Store",
        source_url="https://play.google.com/store/apps/details?id=gold8",
        user_quote="When I type 'receipt' it gives me 500 images in a huge grid with no way to filter by month.",
        user_intent="Filter large candidate set",
        failure_stage=FailureStage.STAGE_5,
        failure_category=FailureCategory.F,
        evidence_strength=EvidenceStrength.HIGH,
    )
    extra_3 = EvidenceRecord(
        evidence_id="EV-GOLD-009",
        source_platform="YouTube",
        source_url="https://youtube.com/watch?v=gold9",
        user_quote="I typed 'concert with my sister' but Google Photos doesn't understand relationship words like sister.",
        user_intent="Search by relationship",
        failure_stage=FailureStage.STAGE_2,
        failure_category=FailureCategory.J,
        evidence_strength=EvidenceStrength.HIGH,
    )
    extra_4 = EvidenceRecord(
        evidence_id="EV-GOLD-010",
        source_platform="X/Twitter",
        source_url="https://x.com/user/status/gold10",
        user_quote="Gave up searching for the photo because it returned zero results.",
        user_intent="Find lost photo",
        failure_stage=FailureStage.STAGE_6,
        failure_category=FailureCategory.A,
        evidence_strength=EvidenceStrength.LOW,
    )

    records.extend([extra_1, extra_2, extra_3, extra_4])
    return records[:10]


def test_taxonomy_classifier_gold_standard_benchmark():
    records = create_gold_standard_benchmark_records()
    assert len(records) == 10

    classifier = TaxonomyClassifier()
    classified_records = classifier.classify_batch(records)

    assert len(classified_records) == 10

    valid_stages = set(FailureStage)
    valid_categories = set(FailureCategory)
    valid_clue_types = set(MemoryClueType)
    valid_claim_tags = set(ClaimTag)
    valid_confidence_labels = set(EvidenceStrength)

    # 100% assignment check across all 10 benchmark records
    for rec in classified_records:
        assert rec.failure_stage in valid_stages
        assert rec.failure_category in valid_categories
        assert rec.memory_clue_type in valid_clue_types
        assert rec.claim_tag in valid_claim_tags
        assert rec.evidence_strength in valid_confidence_labels

        # Verify taxonomy descriptions
        assert len(rec.failure_stage.describe()) > 10
        assert len(rec.failure_category.describe()) > 5
        assert len(rec.memory_clue_type.describe()) > 5


def test_taxonomy_classifier_specific_mappings():
    classifier = TaxonomyClassifier()

    rec_abandonment = EvidenceRecord(
        evidence_id="EV-TEST-AB",
        source_platform="Reddit",
        source_url="https://reddit.com/test",
        user_quote="I searched for an hour and gave up looking for the photo.",
        user_intent="Find photo",
        failure_stage=FailureStage.STAGE_1,
        failure_category=FailureCategory.A,
    )
    classified_ab = classifier.classify_record(rec_abandonment)
    assert classified_ab.failure_stage == FailureStage.STAGE_6  # Must classify as Abandonment

    rec_grid = EvidenceRecord(
        evidence_id="EV-TEST-GRID",
        source_platform="App Store",
        source_url="https://apple.com/test",
        user_quote="Returned 500 images in a huge grid with tiny thumbnails.",
        user_intent="Find receipt",
        failure_stage=FailureStage.STAGE_1,
        failure_category=FailureCategory.A,
    )
    classified_grid = classifier.classify_record(rec_grid)
    assert classified_grid.failure_stage == FailureStage.STAGE_4  # Must classify as Evaluation Gap
