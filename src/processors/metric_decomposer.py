"""
Business Metric Funnel Decomposition Engine.
Maps classified failure stages onto the standard retrieval funnel and correlates failure loci
with diagnostic proxy business metrics (search-to-tap, query reformulation, abandonment rate).
Adheres strictly to prd.md Section 2 (FR-5), Section 5 (Section 6 of report), and research-brief.md Section 13.
"""

import logging
from typing import List, Dict
from pydantic import BaseModel, Field
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureStage, ClaimTag

logger = logging.getLogger("DiscoveryEngine.MetricDecomposer")


class FunnelStageMetric(BaseModel):
    stage_number: int = Field(..., ge=1, le=7)
    stage_name: str
    funnel_step: str
    evidence_count: int = 0
    percentage: float = 0.0
    mapped_proxy_metric: str
    diagnostic_metric_description: str
    claim_tag: ClaimTag = ClaimTag.INFERRED
    product_implication: str


class FunnelDecomposition(BaseModel):
    stages: List[FunnelStageMetric] = Field(default_factory=list)
    total_evidence_count: int = 0
    bottleneck_stage_number: int = 2
    bottleneck_stage_name: str = ""
    bottleneck_concentration_pct: float = 0.0
    summary_takeaway: str = ""


class BusinessMetricDecomposer:
    """
    Decomposes retrieval failure evidence across the 7 funnel stages and maps telemetry proxy metrics.
    """

    # Static funnel mapping definition per prd.md & research-brief.md
    STAGE_METRIC_MAP = {
        1: {
            "step": "User Memory -> Expression",
            "name": "Stage 1: User Cannot Express the Memory (Expression Gap)",
            "metric": "Initial Query Specificity Rate & Formulation Time",
            "desc": "Percentage of initial queries containing low-specificity or non-standard descriptive terms.",
            "implication": "User retains memory fragments but lacks keywords; requires guided query prompts.",
        },
        2: {
            "step": "Ability to Express -> System Understanding",
            "name": "Stage 2: System Cannot Understand the Expressed Memory (Intent Mapping Gap)",
            "metric": "Query Reformulation Count per Session",
            "desc": "Average number of query tweaks per session before tap or give-up.",
            "implication": "Parser fails to map descriptive phrases to visual index attributes; requires semantic query parser.",
        },
        3: {
            "step": "System Understanding -> Candidate Retrieval",
            "name": "Stage 3: System Understands but Retrieves Poor Candidates (Ranking & Recall Gap)",
            "metric": "Candidate Recall Precision @ K & Zero-Result Rate",
            "desc": "Percentage of ambiguous searches returning zero or irrelevant candidate items.",
            "implication": "Target media unindexed or ranked below fold; requires multimodal embedding index.",
        },
        4: {
            "step": "Candidate Retrieval -> Result Evaluation",
            "name": "Stage 4: Relevant Candidates Exist but Are Hard to Evaluate (Recognition & UI Gap)",
            "metric": "Search-to-Tap Success Rate & Grid Dwell Time",
            "desc": "Percentage of search sessions resulting in a target photo tap from result grid.",
            "implication": "Dense grid thumbnails conceal target photo; requires visual highlighting & snippet previews.",
        },
        5: {
            "step": "Result Evaluation -> Search Refinement",
            "name": "Stage 5: User Cannot Effectively Refine a Bad First Query (Refinement Gap)",
            "metric": "Refinement Tool Engagement & Filter Pivot Rate",
            "desc": "Frequency of user engagement with filter chips or suggested query pivots.",
            "implication": "Lack of progressive search filters forces dead-end searches; requires active filter suggestions.",
        },
        6: {
            "step": "Search Refinement -> Session Outcome",
            "name": "Stage 6: User Abandons Before Resolving (Abandonment Locus)",
            "metric": "Search Session Abandonment Rate without Tap",
            "desc": "Percentage of search sessions terminated without opening any photo.",
            "implication": "High cumulative friction leads to search give-up; directly drives user dissatisfaction.",
        },
        7: {
            "step": "Other Loci",
            "name": "Stage 7: Other (Unpredicted Failure Loci)",
            "metric": "Unclassified Friction Index",
            "desc": "Prevalence of unpredicted system issues (e.g. cross-account sync, missing backup).",
            "implication": "Infrastructure or cross-device synchronisation issues.",
        },
    }

    def decompose(self, records: List[EvidenceRecord]) -> FunnelDecomposition:
        """
        Decomposes evidence records across the funnel stages and calculates diagnostic metrics.
        """
        total_count = len(records)
        stage_counts: Dict[int, int] = {s: 0 for s in range(1, 8)}

        for r in records:
            stage_num = int(r.failure_stage)
            if 1 <= stage_num <= 7:
                stage_counts[stage_num] += 1
            else:
                stage_counts[7] += 1

        stage_metrics: List[FunnelStageMetric] = []

        for stage_num in range(1, 8):
            count = stage_counts[stage_num]
            pct = round((count / total_count * 100.0), 1) if total_count > 0 else 0.0
            info = self.STAGE_METRIC_MAP[stage_num]

            metric_item = FunnelStageMetric(
                stage_number=stage_num,
                stage_name=info["name"],
                funnel_step=info["step"],
                evidence_count=count,
                percentage=pct,
                mapped_proxy_metric=info["metric"],
                diagnostic_metric_description=info["desc"],
                claim_tag=ClaimTag.INFERRED,  # Qualitative public evidence mapped to telemetry proxy
                product_implication=info["implication"],
            )
            stage_metrics.append(metric_item)

        # Identify bottleneck stage (stage with maximum evidence concentration)
        bottleneck_num = max(stage_counts.items(), key=lambda x: x[1])[0] if total_count > 0 else 2
        bottleneck_info = self.STAGE_METRIC_MAP[bottleneck_num]
        bottleneck_count = stage_counts[bottleneck_num]
        bottleneck_pct = round((bottleneck_count / total_count * 100.0), 1) if total_count > 0 else 0.0

        summary = (
            f"Retrieval failures concentrate heavily at {bottleneck_info['name']} "
            f"accounting for {bottleneck_pct}% of total evidence ({bottleneck_count}/{total_count} records). "
            f"Primary proxy metric to track: '{bottleneck_info['metric']}'."
        )

        return FunnelDecomposition(
            stages=stage_metrics,
            total_evidence_count=total_count,
            bottleneck_stage_number=bottleneck_num,
            bottleneck_stage_name=bottleneck_info["name"],
            bottleneck_concentration_pct=bottleneck_pct,
            summary_takeaway=summary,
        )
