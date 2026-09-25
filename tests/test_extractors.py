"""
Unit tests for EvidenceExtractor.
Phase 4 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from pathlib import Path
from src.collectors.base import RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector
from src.processors.extractor import EvidenceExtractor
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength


def test_extractor_single_record():
    raw_item = RawEvidenceItem(
        raw_id="RAW-TEST-001",
        source_platform="Reddit",
        source_url="https://www.reddit.com/r/googlephotos/comments/sample_cafe",
        source_date="2026-04-12",
        raw_text="I spent an hour looking for that small café we went to during our Goa trip last year. I know we were sitting outside on blue chairs, but I can't remember the café name or exact date. I searched 'Goa café' and 'Goa restaurant' in Google Photos, but it only showed generic beach photos.",
        author_or_user="u/photo_traveler",
        search_query="can't find old photos"
    )

    extractor = EvidenceExtractor()
    record = extractor.extract_record(raw_item)

    assert isinstance(record, EvidenceRecord)
    assert record.evidence_id == "EV-TEST-001"
    assert record.source_platform == "Reddit"
    assert record.source_url == raw_item.source_url
    assert record.source_date == "2026-04-12"

    # Verify Zero Fabrication: user_quote must be substring of raw_text
    assert record.user_quote.replace("...", "") in raw_item.raw_text

    # Verify 19 schema fields populated
    fields_dict = record.get_19_fields_dict()
    assert len(fields_dict) == 19
    assert fields_dict["failure_stage"] in [1, 2, 3, 4, 5, 6, 7]
    assert fields_dict["failure_category"] in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    assert "Goa" in record.remembered_clues[0] or "café" in record.remembered_clues[0] or "outdoors" in record.remembered_clues[0]
    assert len(record.forgotten_clues) > 0


def test_extractor_zero_fabrication_rule():
    raw_item = RawEvidenceItem(
        raw_id="RAW-TEST-002",
        source_platform="Google Play Store",
        source_url="https://play.google.com/store/apps/details?id=sample",
        source_date="2026-03-20",
        raw_text="I needed to find a photo of a prescription medicine bottle I took last year when I was sick. I typed 'medicine bottle' and 'sick' but zero results came up.",
        author_or_user="Test User",
        search_query="forgot when photo was taken"
    )

    extractor = EvidenceExtractor()
    record = extractor.extract_record(raw_item)

    # Verbatim quote check: MUST be contained within input raw_text
    quote_prefix = record.user_quote.split("...")[0]
    assert quote_prefix in raw_item.raw_text


def test_extractor_batch_sample_dataset():
    mock_file = Path("data/raw_inputs/sample_evidence.json")
    assert mock_file.exists()

    collector = FileMockCollector(filepath=mock_file)
    raw_items = collector.collect(queries=["test"])
    assert len(raw_items) >= 5

    extractor = EvidenceExtractor()
    records = extractor.extract_batch(raw_items)

    assert len(records) == len(raw_items)

    expected_19_keys = {
        "source_platform", "source_url", "source_date", "user_quote", "user_intent",
        "remembered_clues", "forgotten_clues", "query_attempted", "search_strategy",
        "outcome_description", "perceived_failure_reason", "photo_eventually_found",
        "workaround_used", "emotional_behavioral_consequence", "failure_stage",
        "failure_category", "underlying_user_need", "evidence_strength", "notes"
    }

    for record in records:
        assert isinstance(record, EvidenceRecord)
        assert record.source_url.startswith("http")
        assert len(record.user_quote) > 10
        fields = record.get_19_fields_dict()
        assert set(fields.keys()) == expected_19_keys
