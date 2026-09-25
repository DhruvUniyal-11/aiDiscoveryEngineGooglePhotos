"""
Incident Deduplication Engine.
Detects and merges duplicate posts, crossposts, or repeated discussions describing the identical underlying incident across platforms.
Adheres strictly to prd.md Section 6 Rule 4 (Mandatory Deduplication).
"""

import logging
from typing import List, Set
from urllib.parse import urlparse, parse_qs, urlunparse
from difflib import SequenceMatcher

from src.models.evidence import EvidenceRecord
from src.models.taxonomy import EvidenceStrength

logger = logging.getLogger("DiscoveryEngine.Deduplicator")


class EvidenceDeduplicator:
    def __init__(self, similarity_threshold: float = 0.80):
        self.similarity_threshold = similarity_threshold

    def canonicalize_url(self, url: str) -> str:
        """
        Normalizes URLs by removing tracking query params, trailing slashes, and anchors.
        """
        if not url:
            return ""
        parsed = urlparse(url.strip())
        # Clean query parameters
        clean_path = parsed.path.rstrip("/")
        # Reconstruct clean URL
        clean_url = urlunparse((parsed.scheme, parsed.netloc.lower(), clean_path, "", "", ""))
        return clean_url

    def compute_quote_similarity(self, text1: str, text2: str) -> float:
        """
        Computes text similarity ratio between two quotes or user descriptions.
        """
        if not text1 or not text2:
            return 0.0
        matcher = SequenceMatcher(None, text1.lower().strip(), text2.lower().strip())
        return matcher.ratio()

    def are_duplicates(self, rec1: EvidenceRecord, rec2: EvidenceRecord) -> bool:
        """
        Determines whether two EvidenceRecord instances represent the same underlying incident.
        """
        # Rule 1: Exact canonical URL match
        url1 = self.canonicalize_url(rec1.source_url)
        url2 = self.canonicalize_url(rec2.source_url)
        if url1 and url2 and url1 == url2:
            return True

        # Rule 2: High user quote similarity
        quote_sim = self.compute_quote_similarity(rec1.user_quote, rec2.user_quote)
        if quote_sim >= self.similarity_threshold:
            return True

        # Rule 3: High user intent and query similarity match
        intent_sim = self.compute_quote_similarity(rec1.user_intent, rec2.user_intent)
        if quote_sim >= 0.70 and intent_sim >= 0.85:
            return True

        return False

    def merge_records(self, primary: EvidenceRecord, secondary: EvidenceRecord) -> EvidenceRecord:
        """
        Merges secondary record info into primary record.
        Appends secondary citation URLs to notes and updates clue sets and evidence strength.
        """
        merged_notes = primary.notes or ""

        sec_url = secondary.source_url
        if sec_url and sec_url not in merged_notes and sec_url != primary.source_url:
            merged_notes += f" | [Duplicate Citation Merged: {secondary.source_platform} - {sec_url}]"

        # Combine remembered and forgotten clues without duplicates
        combined_remembered: Set[str] = set(primary.remembered_clues).union(set(secondary.remembered_clues))
        combined_forgotten: Set[str] = set(primary.forgotten_clues).union(set(secondary.forgotten_clues))

        # Upgrade evidence strength if secondary has higher rating
        strength_order = {EvidenceStrength.HIGH: 3, EvidenceStrength.MEDIUM: 2, EvidenceStrength.LOW: 1}
        p_val = strength_order.get(primary.evidence_strength, 2)
        s_val = strength_order.get(secondary.evidence_strength, 2)
        merged_strength = primary.evidence_strength if p_val >= s_val else secondary.evidence_strength

        primary.notes = merged_notes
        primary.remembered_clues = list(combined_remembered)
        primary.forgotten_clues = list(combined_forgotten)
        primary.evidence_strength = merged_strength

        return primary

    def deduplicate_records(self, records: List[EvidenceRecord]) -> List[EvidenceRecord]:
        """
        Deduplicates a list of EvidenceRecords, returning unique records with merged duplicate citations.
        """
        if not records:
            return []

        unique_records: List[EvidenceRecord] = []

        for rec in records:
            is_merged = False
            for existing in unique_records:
                if self.are_duplicates(existing, rec):
                    logger.info(f"Deduplicating record {rec.evidence_id} into primary {existing.evidence_id}")
                    self.merge_records(existing, rec)
                    is_merged = True
                    break

            if not is_merged:
                unique_records.append(rec)

        return unique_records
