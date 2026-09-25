"""
Taxonomy Classification Engine.
Classifies EvidenceRecord instances against the 7 Funnel Failure Stages, 12 Core Problem Categories,
9 Memory Clue Types, Claim Tags ([Observed], [Inferred], [Hypothesis]), and Confidence Labels.
Adheres strictly to prd.md Section 4 and research-brief.md Section 7 & 8.
"""

import logging
from typing import List
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import (
    FailureStage,
    FailureCategory,
    MemoryClueType,
    EvidenceStrength,
    ClaimTag,
)

logger = logging.getLogger("DiscoveryEngine.Classifier")


class TaxonomyClassifier:
    """
    Classifies EvidenceRecord instances against official Google Photos vague-memory research taxonomies.
    """

    def classify_record(self, record: EvidenceRecord) -> EvidenceRecord:
        """
        Refines and validates taxonomy stage, category, memory clue type, claim tag, and confidence label.
        """
        combined_text = (
            f"{record.user_quote} {record.user_intent} {record.outcome_description} "
            f"{record.perceived_failure_reason} {record.workaround_used} "
            f"{record.emotional_behavioral_consequence}"
        ).lower()

        # 1. Failure Stage Classification (Stages 1 through 7)
        record.failure_stage = self._classify_stage(combined_text)

        # 2. Failure Category Classification (Categories A through L)
        record.failure_category = self._classify_category(combined_text, record.failure_stage)

        # 3. Memory Clue Type Classification (Types 1 through 9)
        record.memory_clue_type = self._classify_memory_clue_type(combined_text)

        # 4. Claim Tagging ([Observed], [Inferred], [Hypothesis])
        record.claim_tag = self._determine_claim_tag(record)

        # 5. Confidence Labeling (High, Medium, Low)
        record.evidence_strength = self._evaluate_confidence_label(record)

        return record

    def classify_batch(self, records: List[EvidenceRecord]) -> List[EvidenceRecord]:
        """
        Classifies a list of EvidenceRecords in batch.
        """
        return [self.classify_record(r) for r in records]

    def _classify_stage(self, text: str) -> FailureStage:
        if any(w in text for w in ["gave up", "abandoned", "gave up looking", "searched my email", "opened apple photos"]):
            return FailureStage.STAGE_6  # Stage 6: User Abandons Before Resolving
        elif any(w in text for w in ["huge grid", "500 images", "dense grid", "thumbnail", "opening every single"]):
            return FailureStage.STAGE_4  # Stage 4: Relevant Candidates Exist but Are Hard to Evaluate
        elif any(w in text for w in ["filter", "narrow down", "progressive search", "refine"]):
            return FailureStage.STAGE_5  # Stage 5: User Cannot Effectively Refine a Bad First Query
        elif any(w in text for w in ["doesn't understand", "parser", "generic beach", "misinterpret"]):
            return FailureStage.STAGE_2  # Stage 2: System Cannot Understand the Expressed Memory
        elif any(w in text for w in ["zero results", "returned nothing", "0 results", "empty"]):
            return FailureStage.STAGE_3  # Stage 3: System Understands but Retrieves Poor Candidates
        elif any(w in text for w in ["can't remember", "don't know exact", "lacks words", "fragmentary"]):
            return FailureStage.STAGE_1  # Stage 1: User Cannot Express the Memory
        return FailureStage.STAGE_2  # Default Stage 2

    def _classify_category(self, text: str, stage: FailureStage) -> FailureCategory:
        if any(w in text for w in ["ticket", "receipt", "screenshot", "pnr", "ocr", "invoice", "text"]):
            return FailureCategory.L  # L. Text / Document Memory Problem
        elif any(w in text for w in ["goa", "café", "restaurant", "place", "city", "location", "beach"]):
            return FailureCategory.H  # H. Location Uncertainty
        elif any(w in text for w in ["sick last year", "exact date", "month", "timestamp", "year ago"]):
            return FailureCategory.G  # G. Temporal Uncertainty
        elif any(w in text for w in ["birthday", "concert", "party", "event", "vacation"]):
            return FailureCategory.I  # I. Context / Event Memory Problem
        elif any(w in text for w in ["sister", "friend", "roommate", "family", "tag", "face"]):
            return FailureCategory.J  # J. Relationship / People Memory Problem
        elif any(w in text for w in ["blue", "outside", "patio", "color", "sitting"]):
            return FailureCategory.K  # K. Visual Memory Problem
        elif stage == FailureStage.STAGE_1:
            return FailureCategory.B  # B. Query Expression Problem
        elif stage == FailureStage.STAGE_5:
            return FailureCategory.F  # F. Search Refinement Problem
        return FailureCategory.A  # A. Memory / Recall Problem

    def _classify_memory_clue_type(self, text: str) -> MemoryClueType:
        if any(w in text for w in ["sister", "friend", "roommate", "family", "group"]):
            return MemoryClueType.PEOPLE
        elif any(w in text for w in ["goa", "café", "restaurant", "place", "location"]):
            return MemoryClueType.PLACE
        elif any(w in text for w in ["last year", "date", "timestamp", "sick"]):
            return MemoryClueType.TIME
        elif any(w in text for w in ["birthday", "concert", "party", "trip"]):
            return MemoryClueType.EVENT
        elif any(w in text for w in ["medicine", "bottle", "cup", "car"]):
            return MemoryClueType.OBJECT
        elif any(w in text for w in ["ticket", "receipt", "pnr", "ocr"]):
            return MemoryClueType.TEXT
        elif any(w in text for w in ["blue", "outside", "patio", "lighting"]):
            return MemoryClueType.VISUAL
        return MemoryClueType.EVENT

    def _determine_claim_tag(self, record: EvidenceRecord) -> ClaimTag:
        """
        Assigns claim tag based on evidence directness per prd.md Section 6 Rule 2.
        """
        if record.user_quote and len(record.user_quote) > 15:
            return ClaimTag.OBSERVED
        elif record.underlying_user_need:
            return ClaimTag.INFERRED
        return ClaimTag.HYPOTHESIS

    def _evaluate_confidence_label(self, record: EvidenceRecord) -> EvidenceStrength:
        """
        Evaluates evidence confidence level (High, Medium, Low) per prd.md Section 6 Rule 5.
        """
        text = record.user_quote
        has_url = record.source_url.startswith("http")
        has_duplicate_citation = "Duplicate Citation" in (record.notes or "")

        if has_duplicate_citation or (len(text) > 120 and has_url):
            return EvidenceStrength.HIGH
        elif len(text) > 50 and has_url:
            return EvidenceStrength.MEDIUM
        return EvidenceStrength.LOW
