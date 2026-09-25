"""
Unit tests for Incident Deduplication Engine.
Phase 5 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength
from src.processors.deduplicator import EvidenceDeduplicator


def create_base_record(evidence_id: str, platform: str, url: str, quote: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        source_platform=platform,
        source_url=url,
        source_date="2026-05-01",
        user_quote=quote,
        user_intent="Retrieve photo of café in Goa",
        remembered_clues=["location: Goa", "place: café"],
        forgotten_clues=["exact date", "place name"],
        query_attempted="Goa café",
        search_strategy="Vague keyword search",
        outcome_description="Zero results returned",
        perceived_failure_reason="Search parser failed",
        failure_stage=FailureStage.STAGE_2,
        failure_category=FailureCategory.H,
        evidence_strength=EvidenceStrength.MEDIUM,
    )


def test_canonicalize_url():
    dedup = EvidenceDeduplicator()
    url1 = "HTTPS://WWW.REDDIT.COM/r/googlephotos/comments/123/?"
    url2 = "https://www.reddit.com/r/googlephotos/comments/123?utm_source=share"

    assert dedup.canonicalize_url(url1) == "https://www.reddit.com/r/googlephotos/comments/123"
    assert dedup.canonicalize_url(url2) == "https://www.reddit.com/r/googlephotos/comments/123"


def test_deduplicate_exact_url_duplicates():
    dedup = EvidenceDeduplicator()

    rec1 = create_base_record(
        "EV-001", "Reddit",
        "https://www.reddit.com/r/googlephotos/comments/123/",
        "I spent an hour looking for that small café we went to during our Goa trip last year."
    )
    rec2 = create_base_record(
        "EV-002", "Reddit Crosspost",
        "https://www.reddit.com/r/googlephotos/comments/123?utm_source=share",
        "I spent an hour looking for that small café we went to during our Goa trip last year."
    )

    records = [rec1, rec2]
    deduped = dedup.deduplicate_records(records)

    assert len(deduped) == 1
    assert deduped[0].evidence_id == "EV-001"
    assert "EV-001" in deduped[0].evidence_id


def test_deduplicate_similar_quote_crossposts():
    dedup = EvidenceDeduplicator(similarity_threshold=0.80)

    rec1 = create_base_record(
        "EV-010", "Reddit",
        "https://reddit.com/r/googlephotos/comments/abc",
        "I needed to find a photo of a prescription medicine bottle I took last year when I was sick. I typed medicine bottle and sick but zero results came up."
    )
    rec2 = create_base_record(
        "EV-011", "Twitter",
        "https://x.com/user/status/987654321",
        "I needed to find a photo of a prescription medicine bottle I took last year when I was sick. I typed medicine bottle and sick but zero results came up!"
    )

    records = [rec1, rec2]
    deduped = dedup.deduplicate_records(records)

    assert len(deduped) == 1
    merged_rec = deduped[0]
    assert merged_rec.evidence_id == "EV-010"
    assert "https://x.com/user/status/987654321" in merged_rec.notes
    assert "Twitter" in merged_rec.notes


def test_deduplicate_distinct_records_kept():
    dedup = EvidenceDeduplicator()

    rec1 = create_base_record(
        "EV-100", "Reddit",
        "https://reddit.com/r/googlephotos/comments/goa_cafe",
        "I spent an hour looking for that small café we went to during our Goa trip last year."
    )
    rec2 = create_base_record(
        "EV-101", "Google Play Store",
        "https://play.google.com/store/apps/details?id=sample",
        "Search is terrible when you don't know the exact date. Needed prescription medicine bottle photo."
    )

    records = [rec1, rec2]
    deduped = dedup.deduplicate_records(records)

    assert len(deduped) == 2
    assert deduped[0].evidence_id == "EV-100"
    assert deduped[1].evidence_id == "EV-101"
