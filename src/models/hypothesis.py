"""
Pydantic data model for Falsifiable User Interview Hypotheses.
Adheres strictly to prd.md Section 2 (FR-6), Section 5 (Section 11 of report), Section 8 (Item 11),
and research-brief.md Section 20 (Section 12).
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.taxonomy import ClaimTag


class InterviewHypothesis(BaseModel):
    hypothesis_id: str = Field(..., description="Unique hypothesis identifier (e.g. HYP-001)")
    hypothesis_statement: str = Field(..., description="Clear, testable statement of belief regarding retrieval failure")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of supporting evidence records")
    falsification_condition: str = Field(..., description="Explicit behavioral or recall condition that falsifies hypothesis")
    interview_question: str = Field(..., description="Target question to ask during 5-6 person user interviews")
    behavioral_task: str = Field(..., description="Observational task for participant to attempt during interview")
    target_problem_cluster_id: Optional[str] = Field(default=None, description="Mapped problem cluster ID")
    claim_tag: ClaimTag = Field(default=ClaimTag.HYPOTHESIS, description="Mandatory claim tag ([Hypothesis])")
