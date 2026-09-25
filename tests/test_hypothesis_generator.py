"""
Unit tests for Falsifiable Hypothesis Generation Engine.
Phase 9 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from src.models.problem_cluster import ProblemCluster
from src.models.hypothesis import InterviewHypothesis
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength, ClaimTag
from src.processors.hypothesis_generator import HypothesisGenerator


def create_sample_clusters() -> list[ProblemCluster]:
    return [
        ProblemCluster(
            cluster_id="CLUSTER-01",
            problem_name="Fragmentary Location Context without Exact Business Name",
            description="Users remember broad spatial setting but lack geotag or place name.",
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.H,
            evidence_ids=["EV-LOC-001", "EV-LOC-002", "EV-LOC-003"],
            evidence_count=3,
        ),
        ProblemCluster(
            cluster_id="CLUSTER-02",
            problem_name="Unanchored Relative Temporal & Life Event Memory",
            description="Users recall relative life phases but forget exact calendar dates.",
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.G,
            evidence_ids=["EV-TIME-001", "EV-TIME-002"],
            evidence_count=2,
        ),
        ProblemCluster(
            cluster_id="CLUSTER-03",
            problem_name="Unindexed Screenshot & Document OCR Retrieval Breakdown",
            description="Users search for text printed on screenshots or receipts.",
            failure_stage=FailureStage.STAGE_3,
            failure_category=FailureCategory.L,
            evidence_ids=["EV-OCR-001", "EV-OCR-002"],
            evidence_count=2,
        ),
    ]


def test_hypothesis_generator_count_and_schema_completeness():
    clusters = create_sample_clusters()
    generator = HypothesisGenerator()

    hypotheses = generator.generate_hypotheses(clusters)

    # Must produce between 8 and 12 hypotheses per PRD FR-6 & §5 Section 11
    assert 8 <= len(hypotheses) <= 12

    for hyp in hypotheses:
        assert isinstance(hyp, InterviewHypothesis)
        assert hyp.hypothesis_id.startswith("HYP-")
        assert len(hyp.hypothesis_statement) > 20
        assert len(hyp.supporting_evidence_ids) > 0
        assert len(hyp.falsification_condition) > 20
        assert len(hyp.interview_question) > 15
        assert len(hyp.behavioral_task) > 15
        assert hyp.claim_tag == ClaimTag.HYPOTHESIS


def test_hypothesis_falsification_conditions():
    clusters = create_sample_clusters()
    generator = HypothesisGenerator()
    hypotheses = generator.generate_hypotheses(clusters)

    for hyp in hypotheses:
        # Falsification condition must be explicit and non-empty
        assert "Falsified if" in hyp.falsification_condition or "falsified" in hyp.falsification_condition.lower()
        # Must map to supporting evidence IDs
        assert isinstance(hyp.supporting_evidence_ids, list)
        assert len(hyp.supporting_evidence_ids) >= 1
