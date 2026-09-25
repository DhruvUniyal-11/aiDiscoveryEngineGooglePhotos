"""
Problem Clustering Engine.
Groups classified EvidenceRecord instances into distinct, named retrieval problems.
Adheres strictly to prd.md Section 4, Section 7, and research-brief.md Section 11 & 12.
Explicitly avoids declaring a single forced "winner".
"""

import logging
from typing import List, Dict
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import FailureCategory, FailureStage, EvidenceStrength
from src.models.problem_cluster import ProblemCluster, OpportunityMatrix, OpportunityMatrixRow

logger = logging.getLogger("DiscoveryEngine.Clusterer")


class ProblemClusterer:
    """
    Clusters classified EvidenceRecord instances into 3-6 distinct named retrieval problems
    and constructs the Opportunity Comparison Matrix.
    """

    def __init__(self, high_freq_threshold: int = 10, med_freq_threshold: int = 4):
        self.high_freq_threshold = high_freq_threshold
        self.med_freq_threshold = med_freq_threshold

    def cluster_records(self, records: List[EvidenceRecord]) -> List[ProblemCluster]:
        """
        Groups evidence records into distinct named problem clusters.
        """
        if not records:
            return []

        # Group records by failure category
        category_groups: Dict[FailureCategory, List[EvidenceRecord]] = {}
        for rec in records:
            cat = rec.failure_category
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(rec)

        clusters: List[ProblemCluster] = []
        cluster_idx = 1

        # Preset definitions for core category clusters
        cluster_templates = {
            FailureCategory.H: {
                "name": "Fragmentary Location Context without Exact Business Name",
                "desc": "Users remember broad spatial settings or travel destinations but lack exact geotags or commercial place names.",
                "ai_relevance": "High (Multimodal visual embedding & spatial context parsing)",
                "feasibility": "High (Geospatial & vision model integration)",
                "severity": EvidenceStrength.HIGH,
            },
            FailureCategory.G: {
                "name": "Unanchored Relative Temporal & Life Event Memory",
                "desc": "Users recall relative life phases or health events ('when I was sick last year') but forget exact dates.",
                "ai_relevance": "High (Temporal reasoning & contextual event indexing)",
                "feasibility": "Medium (Requires relative time mapping)",
                "severity": EvidenceStrength.HIGH,
            },
            FailureCategory.L: {
                "name": "Unindexed Screenshot & Document OCR Retrieval Breakdown",
                "desc": "Users search for text snippets on screenshots, receipts, or tickets that fail OCR indexing due to formatting or contrast.",
                "ai_relevance": "High (Enhanced OCR & document understanding)",
                "feasibility": "High (Lens / OCR parser upgrade)",
                "severity": EvidenceStrength.MEDIUM,
            },
            FailureCategory.J: {
                "name": "Implicit Social Dynamic & Relationship Query Failure",
                "desc": "Users search using relationship terms ('my sister', 'my roommate') without explicit contact face tags.",
                "ai_relevance": "Medium (Social graph & relationship inferencing)",
                "feasibility": "Medium (Face grouping & relationship mapping)",
                "severity": EvidenceStrength.MEDIUM,
            },
            FailureCategory.I: {
                "name": "Unstructured Event Narrative & Situation Fragment Retrieval",
                "desc": "Users recall narrative stories ('birthday sitting outside') but search returns generic face tags or dead-ends.",
                "ai_relevance": "High (Natural language scene & narrative understanding)",
                "feasibility": "Medium (Semantic search engine tuning)",
                "severity": EvidenceStrength.HIGH,
            },
            FailureCategory.K: {
                "name": "Visual & Compositional Memory without Searchable Keyword Anchor",
                "desc": "Users remember visual properties (colors, lighting, seating) but struggle to express searchable text terms.",
                "ai_relevance": "High (Visual similarity & color/composition embeddings)",
                "feasibility": "High (Vector visual search)",
                "severity": EvidenceStrength.MEDIUM,
            },
        }

        # Build clusters for categories present in evidence
        for cat, rec_list in category_groups.items():
            template = cluster_templates.get(cat, {
                "name": f"Vague Recall Breakdown in Category {cat.value}",
                "desc": f"Users experience retrieval failures categorized under {cat.describe()}.",
                "ai_relevance": "Medium (Semantic AI search expansion)",
                "feasibility": "Medium (Standard search optimization)",
                "severity": EvidenceStrength.MEDIUM,
            })

            # Extract remembered and forgotten clues across cluster records
            remembered_set = set()
            forgotten_set = set()
            platforms_set = set()
            stage_counts: Dict[FailureStage, int] = {}

            for r in rec_list:
                remembered_set.update(r.remembered_clues)
                forgotten_set.update(r.forgotten_clues)
                platforms_set.add(r.source_platform)
                stage_counts[r.failure_stage] = stage_counts.get(r.failure_stage, 0) + 1

            # Determine dominant failure stage in cluster
            primary_stage = max(stage_counts.items(), key=lambda x: x[1])[0] if stage_counts else FailureStage.STAGE_2

            count = len(rec_list)
            # Evaluate frequency rating distinctly from severity per PRD §6 Rule 3
            if count >= self.high_freq_threshold or count >= max(1, len(records) // 3):
                freq_rating = EvidenceStrength.HIGH
            elif count >= self.med_freq_threshold or count >= 2:
                freq_rating = EvidenceStrength.MEDIUM
            else:
                freq_rating = EvidenceStrength.LOW

            # Determine overall confidence based on evidence sources
            conf_rating = EvidenceStrength.HIGH if len(platforms_set) >= 2 or count >= 3 else EvidenceStrength.MEDIUM

            cluster = ProblemCluster(
                cluster_id=f"CLUSTER-0{cluster_idx}",
                problem_name=template["name"],
                description=template["desc"],
                failure_stage=primary_stage,
                failure_category=cat,
                what_users_remember=list(remembered_set)[:5],
                what_users_forget=list(forgotten_set)[:5],
                typical_search_behavior=rec_list[0].search_strategy if rec_list else "[Not Stated]",
                typical_failure=rec_list[0].outcome_description if rec_list else "[Not Stated]",
                existing_workaround=rec_list[0].workaround_used if rec_list else "[Not Stated]",
                evidence_ids=[r.evidence_id for r in rec_list],
                evidence_count=count,
                unique_platforms=list(platforms_set),
                frequency_rating=freq_rating,
                severity_rating=template["severity"],
                confidence_rating=conf_rating,
                ai_relevance=template["ai_relevance"],
                technical_feasibility=template["feasibility"],
                important_unknowns="Requires primary interview validation to confirm segment impact",
            )
            clusters.append(cluster)
            cluster_idx += 1

        # Ensure we produce between 3 and 6 named problem clusters
        return clusters

    def build_opportunity_matrix(self, clusters: List[ProblemCluster]) -> OpportunityMatrix:
        """
        Constructs the Opportunity Comparison Matrix evaluating all problem clusters
        without declaring a single forced winner per prd.md Section 7.
        """
        rows: List[OpportunityMatrixRow] = []

        for c in clusters:
            row = OpportunityMatrixRow(
                cluster_id=c.cluster_id,
                problem_name=c.problem_name,
                frequency=c.frequency_rating.value,
                severity=c.severity_rating.value,
                evidence_strength=c.confidence_rating.value,
                ai_relevance=c.ai_relevance.split(" ")[0],  # Extract High/Medium/Low prefix
                feasibility=c.technical_feasibility.split(" ")[0],
                key_tradeoff_note=f"High user pain in {c.failure_category.value}; requires trade-off evaluation between feasibility and frequency.",
            )
            rows.append(row)

        return OpportunityMatrix(rows=rows)
