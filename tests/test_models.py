"""
Unit tests for 19-Field EvidenceRecord model, taxonomies, and storage repository.
Phase 2 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
import json
from pathlib import Path
from pydantic import ValidationError

from src.models.evidence import EvidenceRecord
from src.models.taxonomy import (
    FailureStage,
    FailureCategory,
    MemoryClueType,
    PhotoEventuallyFound,
    EvidenceStrength,
    ClaimTag,
)
from src.storage.repository import EvidenceRepository


def create_sample_valid_record(evidence_id: str = "EV-001") -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        source_platform="Reddit",
        source_url="https://reddit.com/r/googlephotos/comments/sample_123",
        source_date="2026-05-15",
        user_quote="I remember that small café we went to during our Goa trip, but Google Photos won't find it.",
        user_intent="Retrieve photo of a small café from Goa vacation",
        remembered_clues=["location: Goa", "place_type: café", "event: vacation"],
        forgotten_clues=["exact date", "place name", "album name"],
        query_attempted="Goa café",
        search_strategy="Vague keyword search",
        outcome_description="Zero relevant results returned; showed generic Goa landmarks",
        perceived_failure_reason="Search doesn't understand generic place descriptors without exact name tag",
        photo_eventually_found=PhotoEventuallyFound.NO,
        workaround_used="Manually scrolled through timeline from June 2025",
        emotional_behavioral_consequence="High frustration; gave up after 15 minutes",
        failure_stage=FailureStage.STAGE_2,  # System Cannot Understand
        failure_category=FailureCategory.H,  # Location Uncertainty
        underlying_user_need="Semantic location search without requiring explicit business name",
        evidence_strength=EvidenceStrength.HIGH,
        notes="High quality post with clear user recall vs system failure distinction",
        claim_tag=ClaimTag.OBSERVED,
        memory_clue_type=MemoryClueType.PLACE,
    )


def test_evidence_record_19_fields_valid():
    rec = create_sample_valid_record("EV-001")
    fields_dict = rec.get_19_fields_dict()

    # Verify all 19 fields exist in dictionary
    expected_19_keys = {
        "source_platform", "source_url", "source_date", "user_quote", "user_intent",
        "remembered_clues", "forgotten_clues", "query_attempted", "search_strategy",
        "outcome_description", "perceived_failure_reason", "photo_eventually_found",
        "workaround_used", "emotional_behavioral_consequence", "failure_stage",
        "failure_category", "underlying_user_need", "evidence_strength", "notes"
    }

    assert set(fields_dict.keys()) == expected_19_keys
    assert fields_dict["source_platform"] == "Reddit"
    assert fields_dict["failure_stage"] == 2
    assert fields_dict["failure_category"] == "H"
    assert fields_dict["photo_eventually_found"] == "No"
    assert fields_dict["evidence_strength"] == "High"


def test_evidence_record_validation_missing_required():
    # Test missing source_url
    with pytest.raises(ValidationError) as exc_info:
        EvidenceRecord(
            source_platform="Play Store",
            source_url="",  # Empty string
            user_quote="Can't find my photo",
            user_intent="Find photo",
            failure_stage=FailureStage.STAGE_1,
            failure_category=FailureCategory.A,
        )
    assert "source_url" in str(exc_info.value)

    # Test missing user_quote
    with pytest.raises(ValidationError) as exc_info:
        EvidenceRecord(
            source_platform="Play Store",
            source_url="https://play.google.com/store/apps/details?id=sample",
            user_quote="   ",  # Whitespace only
            user_intent="Find photo",
            failure_stage=FailureStage.STAGE_1,
            failure_category=FailureCategory.A,
        )
    assert "user_quote" in str(exc_info.value)


def test_evidence_record_validation_invalid_enums():
    # Test invalid failure_stage (e.g. 99)
    with pytest.raises(ValidationError):
        EvidenceRecord(
            source_platform="Play Store",
            source_url="https://play.google.com/store/details?id=123",
            user_quote="Photo search broke",
            user_intent="Find photo",
            failure_stage=99,  # Invalid stage
            failure_category=FailureCategory.A,
        )

    # Test invalid failure_category (e.g. "Z")
    with pytest.raises(ValidationError):
        EvidenceRecord(
            source_platform="Play Store",
            source_url="https://play.google.com/store/details?id=123",
            user_quote="Photo search broke",
            user_intent="Find photo",
            failure_stage=FailureStage.STAGE_1,
            failure_category="Z",  # Invalid category
        )


def test_repository_sqlite_crud(tmp_path):
    db_file = tmp_path / "test_evidence.db"
    repo = EvidenceRepository(db_file)

    rec1 = create_sample_valid_record("EV-001")
    rec2 = create_sample_valid_record("EV-002")
    rec2.source_platform = "Google Play Store"
    rec2.failure_stage = FailureStage.STAGE_5
    rec2.failure_category = FailureCategory.G

    # Save records
    repo.save_record(rec1)
    repo.save_record(rec2)

    assert repo.count_records() == 2

    # Get record
    fetched1 = repo.get_record("EV-001")
    assert fetched1 is not None
    assert fetched1.user_quote == rec1.user_quote
    assert fetched1.failure_stage == FailureStage.STAGE_2
    assert fetched1.failure_category == FailureCategory.H

    # Get all records
    all_recs = repo.get_all_records()
    assert len(all_recs) == 2
    assert all_recs[0].evidence_id == "EV-001"
    assert all_recs[1].evidence_id == "EV-002"


def test_repository_jsonl_export_import(tmp_path):
    db_file = tmp_path / "test_evidence.db"
    repo = EvidenceRepository(db_file)

    rec1 = create_sample_valid_record("EV-001")
    rec2 = create_sample_valid_record("EV-002")
    repo.save_record(rec1)
    repo.save_record(rec2)

    # Export to JSONL
    jsonl_file = tmp_path / "exported_evidence.jsonl"
    exported_path = repo.export_to_jsonl(jsonl_file)
    assert exported_path.exists()

    # Read exported JSONL lines
    lines = exported_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    record_data = json.loads(lines[0])
    assert record_data["evidence_id"] == "EV-001"
    assert record_data["source_platform"] == "Reddit"

    # Import into a clean repository
    new_db_file = tmp_path / "imported_evidence.db"
    new_repo = EvidenceRepository(new_db_file)
    imported_count = new_repo.import_from_jsonl(jsonl_file)
    assert imported_count == 2
    assert new_repo.count_records() == 2

    imported_rec = new_repo.get_record("EV-001")
    assert imported_rec is not None
    assert imported_rec.user_quote == rec1.user_quote
    assert imported_rec.failure_stage == FailureStage.STAGE_2
