"""
Unit tests for Business Metric Funnel Decomposition Engine.
Phase 8 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength, ClaimTag
from src.processors.metric_decomposer import BusinessMetricDecomposer, FunnelDecomposition, FunnelStageMetric


def create_sample_evidence_set() -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []

    # 10 records in Stage 2 (System Understanding) -> Expected Bottleneck
    for i in range(10):
        records.append(EvidenceRecord(
            evidence_id=f"EV-STAGE2-{i}",
            source_platform="Reddit",
            source_url=f"https://reddit.com/r/googlephotos/comments/s2_{i}",
            user_quote=f"Searched for café in Goa #{i} but Google Photos doesn't understand.",
            user_intent="Find Goa café",
            failure_stage=FailureStage.STAGE_2,
            failure_category=FailureCategory.H,
            evidence_strength=EvidenceStrength.HIGH,
        ))

    # 4 records in Stage 6 (Abandonment)
    for i in range(4):
        records.append(EvidenceRecord(
            evidence_id=f"EV-STAGE6-{i}",
            source_platform="Play Store",
            source_url=f"https://play.google.com/store/details?id=s6_{i}",
            user_quote=f"Searched for prescription bottle #{i} and gave up after 15 minutes.",
            user_intent="Find medicine bottle",
            failure_stage=FailureStage.STAGE_6,
            failure_category=FailureCategory.G,
            evidence_strength=EvidenceStrength.MEDIUM,
        ))

    # 3 records in Stage 4 (Result Evaluation)
    for i in range(3):
        records.append(EvidenceRecord(
            evidence_id=f"EV-STAGE4-{i}",
            source_platform="App Store",
            source_url=f"https://apple.com/reviews/s4_{i}",
            user_quote=f"Returned 500 images in a huge grid #{i} with tiny thumbnails.",
            user_intent="Find receipt screenshot",
            failure_stage=FailureStage.STAGE_4,
            failure_category=FailureCategory.L,
            evidence_strength=EvidenceStrength.MEDIUM,
        ))

    # 3 records in Stage 1 (Expression Gap)
    for i in range(3):
        records.append(EvidenceRecord(
            evidence_id=f"EV-STAGE1-{i}",
            source_platform="Google Help",
            source_url=f"https://support.google.com/s1_{i}",
            user_quote=f"Can't remember the words to search for #{i}.",
            user_intent="Vague memory search",
            failure_stage=FailureStage.STAGE_1,
            failure_category=FailureCategory.A,
            evidence_strength=EvidenceStrength.LOW,
        ))

    return records


def test_metric_decomposer_funnel_mapping():
    records = create_sample_evidence_set()
    assert len(records) == 20

    decomposer = BusinessMetricDecomposer()
    decomp = decomposer.decompose(records)

    assert isinstance(decomp, FunnelDecomposition)
    assert decomp.total_evidence_count == 20
    assert len(decomp.stages) == 7

    # Verify stage numbers 1..7 present in order
    for idx, stage in enumerate(decomp.stages, start=1):
        assert isinstance(stage, FunnelStageMetric)
        assert stage.stage_number == idx
        assert len(stage.stage_name) > 10
        assert len(stage.mapped_proxy_metric) > 5
        assert len(stage.diagnostic_metric_description) > 10
        assert stage.claim_tag in [ClaimTag.INFERRED, ClaimTag.OBSERVED]

    # Verify evidence counts sum up to 20
    total_count = sum(s.evidence_count for s in decomp.stages)
    assert total_count == 20

    # Verify percentages sum up to 100%
    total_pct = sum(s.percentage for s in decomp.stages)
    assert pytest.approx(total_pct, 0.1) == 100.0


def test_metric_decomposer_bottleneck_identification():
    records = create_sample_evidence_set()
    decomposer = BusinessMetricDecomposer()
    decomp = decomposer.decompose(records)

    # Stage 2 has 10/20 records = 50.0% -> Must be identified as bottleneck
    assert decomp.bottleneck_stage_number == 2
    assert "Stage 2" in decomp.bottleneck_stage_name
    assert decomp.bottleneck_concentration_pct == 50.0
    assert "Query Reformulation Count" in decomp.summary_takeaway
