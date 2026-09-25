"""
Pydantic model for 19-Field Evidence Record.
Adheres strictly to prd.md Section 3 and research-brief.md Section 6.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from src.models.taxonomy import (
    FailureStage,
    FailureCategory,
    MemoryClueType,
    PhotoEventuallyFound,
    EvidenceStrength,
    ClaimTag,
)


class EvidenceRecord(BaseModel):
    # Metadata & Identifiers
    evidence_id: str = Field(
        default="EV-000",
        description="Unique evidence identifier (e.g. EV-001)"
    )

    # Core 19 Fields (Explicitly Named per prd.md §3 & research-brief.md §6)
    source_platform: str = Field(
        ...,
        description="Field 1: Source platform (Play Store, App Store, Reddit, etc.)"
    )
    source_url: str = Field(
        ...,
        description="Field 2: Canonical source URL (MUST NOT be fabricated)"
    )
    source_date: str = Field(
        default="[Not Stated]",
        description="Field 3: Date of publication or [Not Stated]"
    )
    user_quote: str = Field(
        ...,
        description="Field 4: Verbatim user quote or close paraphrase (MUST NOT be fabricated)"
    )
    user_intent: str = Field(
        ...,
        description="Field 5: Concise description of what the user was trying to find"
    )
    remembered_clues: List[str] = Field(
        default_factory=list,
        description="Field 6: Specific details or clues the user remembered"
    )
    forgotten_clues: List[str] = Field(
        default_factory=list,
        description="Field 7: Crucial metadata or details the user explicitly forgot"
    )
    query_attempted: str = Field(
        default="[Not Stated]",
        description="Field 8: Search term(s) or query string(s) entered by user"
    )
    search_strategy: str = Field(
        default="[Not Stated]",
        description="Field 9: Search strategy used (keyword combo, face filter, Lens, etc.)"
    )
    outcome_description: str = Field(
        default="[Not Stated]",
        description="Field 10: Description of what happened during/after search execution"
    )
    perceived_failure_reason: str = Field(
        default="[Not Stated]",
        description="Field 11: Why the user believes retrieval failed"
    )
    photo_eventually_found: PhotoEventuallyFound = Field(
        default=PhotoEventuallyFound.NO,
        description="Field 12: Retrieval outcome status (Yes, No, Partial, Abandoned)"
    )
    workaround_used: str = Field(
        default="[Not Stated]",
        description="Field 13: Workaround strategy used by user"
    )
    emotional_behavioral_consequence: str = Field(
        default="[Not Stated]",
        description="Field 14: Explicitly stated user reaction/frustration"
    )
    failure_stage: FailureStage = Field(
        ...,
        description="Field 15: Stage of failure in funnel (Stages 1 to 7)"
    )
    failure_category: FailureCategory = Field(
        ...,
        description="Field 16: Primary taxonomy category (Categories A to L)"
    )
    underlying_user_need: str = Field(
        default="[Not Stated]",
        description="Field 17: Latent user requirement synthesis"
    )
    evidence_strength: EvidenceStrength = Field(
        default=EvidenceStrength.MEDIUM,
        description="Field 18: Evidence quality/confidence rating (High, Medium, Low)"
    )
    notes: str = Field(
        default="",
        description="Field 19: Additional researcher annotations or cross-references"
    )

    # Auxiliary Taxonomy Helper Fields
    claim_tag: ClaimTag = Field(
        default=ClaimTag.OBSERVED,
        description="Quality rule claim classification tag ([Observed], [Inferred], [Hypothesis])"
    )
    memory_clue_type: Optional[MemoryClueType] = Field(
        default=None,
        description="Primary memory clue type (Types 1 to 9)"
    )

    @field_validator("source_platform", "source_url", "user_quote", "user_intent")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty")
        return v.strip()

    def get_19_fields_dict(self) -> dict:
        """
        Returns dictionary containing strictly the 19 fields defined in the schema.
        """
        return {
            "source_platform": self.source_platform,
            "source_url": self.source_url,
            "source_date": self.source_date,
            "user_quote": self.user_quote,
            "user_intent": self.user_intent,
            "remembered_clues": self.remembered_clues,
            "forgotten_clues": self.forgotten_clues,
            "query_attempted": self.query_attempted,
            "search_strategy": self.search_strategy,
            "outcome_description": self.outcome_description,
            "perceived_failure_reason": self.perceived_failure_reason,
            "photo_eventually_found": self.photo_eventually_found.value,
            "workaround_used": self.workaround_used,
            "emotional_behavioral_consequence": self.emotional_behavioral_consequence,
            "failure_stage": int(self.failure_stage),
            "failure_category": self.failure_category.value,
            "underlying_user_need": self.underlying_user_need,
            "evidence_strength": self.evidence_strength.value,
            "notes": self.notes,
        }
