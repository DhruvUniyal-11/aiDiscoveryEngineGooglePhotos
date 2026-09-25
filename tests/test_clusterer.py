"""
Unit tests for Problem Clustering Engine and Opportunity Matrix.
Phase 7 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength
from src.processors.clusterer import ProblemClusterer
from src.models.problem_cluster import ProblemCluster, OpportunityMatrix


def create_20_plus_classified_records() -> list[EvidenceRecord]:
    """
    Constructs a dataset of 22 classified EvidenceRecords across categories H, G, L, J, I, K.
    """
    records: list[EvidenceRecord] = []

    # Category H: Location Uncertainty (6 items)
    for i in range(1, 7):
        records.append(EvidenceRecord(
            evidence_id=f"EV-LOC-{i:03d}",
            source_platform="Reddit" if i % 2 == 0 else "Play Store",
            source_url=f"https://reddit.com/r/googlephotos/comments/loc_{i}",
            user_quote=f"Looking for that small café in Goa #{i} sitting outside on blue chairs.",
            user_intent="Find Goa café",
            remembered_clues=["location: Goa", "place: café"],
            forgotten_clues=["exact date", "place name"],
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.H,
            evidence_strength=EvidenceStrength.HIGH if i <= 3 else EvidenceStrength.MEDIUM,
        ))

    # Category G: Temporal Uncertainty (5 items)
    for i in range(1, 6):
        records.append(EvidenceRecord(
            evidence_id=f"EV-TIME-{i:03d}",
            source_platform="Google Help" if i % 2 == 0 else "App Store",
            source_url=f"https://support.google.com/thread/time_{i}",
            user_quote=f"Photo of medicine bottle I took last year when I was sick #{i}.",
            user_intent="Find prescription bottle",
            remembered_clues=["item: medicine bottle", "context: sick last year"],
            forgotten_clues=["exact date", "month"],
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.G,
            evidence_strength=EvidenceStrength.HIGH if i <= 2 else EvidenceStrength.MEDIUM,
        ))

    # Category L: Text / OCR Memory (4 items)
    for i in range(1, 5):
        records.append(EvidenceRecord(
            evidence_id=f"EV-OCR-{i:03d}",
            source_platform="Reddit",
            source_url=f"https://reddit.com/r/techsupport/comments/ocr_{i}",
            user_quote=f"Screenshot of train ticket with PNR number #{i} dark mode.",
            user_intent="Find train ticket PNR",
            remembered_clues=["item: train ticket", "text: PNR"],
            forgotten_clues=["exact date"],
            failure_stage=FailureStage.STAGE_3,
            failure_category=FailureCategory.L,
            evidence_strength=EvidenceStrength.MEDIUM,
        ))

    # Category J: Relationship Memory (4 items)
    for i in range(1, 5):
        records.append(EvidenceRecord(
            evidence_id=f"EV-REL-{i:03d}",
            source_platform="YouTube",
            source_url=f"https://youtube.com/watch?v=rel_{i}",
            user_quote=f"Concert photo with my sister #{i} without tagged face.",
            user_intent="Find concert photo with sister",
            remembered_clues=["people: sister", "event: concert"],
            forgotten_clues=["face tag name"],
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.J,
            evidence_strength=EvidenceStrength.HIGH,
        ))

    # Category I: Event Narrative Context (3 items)
    for i in range(1, 4):
        records.append(EvidenceRecord(
            evidence_id=f"EV-EVENT-{i:03d}",
            source_platform="Forum",
            source_url=f"https://forum.tech/thread/event_{i}",
            user_quote=f"Birthday party sitting outside on patio #{i}.",
            user_intent="Find birthday photo",
            remembered_clues=["event: birthday", "setting: patio"],
            forgotten_clues=["album title"],
            failure_stage=FailureStage.STAGE_5,
            failure_category=FailureCategory.I,
            evidence_strength=EvidenceStrength.MEDIUM,
        ))

    return records


def test_problem_clusterer_20_plus_records():
    records = create_20_plus_classified_records()
    assert len(records) == 22

    clusterer = ProblemClusterer(high_freq_threshold=5, med_freq_threshold=3)
    clusters = clusterer.cluster_records(records)

    # Must produce between 3 and 6 distinct named problem clusters
    assert 3 <= len(clusters) <= 6

    total_evidence_in_clusters = sum(c.evidence_count for c in clusters)
    assert total_evidence_in_clusters == 22

    for cluster in clusters:
        assert isinstance(cluster, ProblemCluster)
        assert cluster.cluster_id.startswith("CLUSTER-")
        assert len(cluster.problem_name) > 10
        assert len(cluster.description) > 20
        assert cluster.evidence_count > 0
        assert len(cluster.evidence_ids) == cluster.evidence_count
        assert cluster.frequency_rating in [EvidenceStrength.HIGH, EvidenceStrength.MEDIUM, EvidenceStrength.LOW]
        assert cluster.severity_rating in [EvidenceStrength.HIGH, EvidenceStrength.MEDIUM, EvidenceStrength.LOW]
        assert cluster.confidence_rating in [EvidenceStrength.HIGH, EvidenceStrength.MEDIUM, EvidenceStrength.LOW]
        assert len(cluster.ai_relevance) > 5
        assert len(cluster.technical_feasibility) > 5


def test_opportunity_matrix_generation():
    records = create_20_plus_classified_records()
    clusterer = ProblemClusterer()
    clusters = clusterer.cluster_records(records)

    matrix = clusterer.build_opportunity_matrix(clusters)
    assert isinstance(matrix, OpportunityMatrix)
    assert len(matrix.rows) == len(clusters)

    for row in matrix.rows:
        assert row.cluster_id.startswith("CLUSTER-")
        assert len(row.problem_name) > 5
        assert row.frequency in ["High", "Medium", "Low"]
        assert row.severity in ["High", "Medium", "Low"]
        assert row.evidence_strength in ["High", "Medium", "Low"]
        assert len(row.key_tradeoff_note) > 10


def test_frequency_vs_severity_disambiguation():
    """
    Verifies PRD Section 6 Rule 3: Frequency and Severity must be distinct dimensions.
    """
    records = create_20_plus_classified_records()
    clusterer = ProblemClusterer()
    clusters = clusterer.cluster_records(records)

    # Verify every cluster maintains separate frequency and severity ratings
    for c in clusters:
        assert hasattr(c, "frequency_rating")
        assert hasattr(c, "severity_rating")
        # Ensure ratings are distinct fields in the model
        dict_rep = c.model_dump()
        assert "frequency_rating" in dict_rep
        assert "severity_rating" in dict_rep
