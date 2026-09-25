"""
Pydantic data models for Problem Clusters and Opportunity Comparison Matrix.
Adheres strictly to prd.md Section 4, Section 7, and research-brief.md Section 11 & 12.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.taxonomy import FailureStage, FailureCategory, EvidenceStrength


class ProblemCluster(BaseModel):
    cluster_id: str = Field(..., description="Unique cluster identifier (e.g. CLUSTER-01)")
    problem_name: str = Field(..., description="Named, distinct retrieval problem name")
    description: str = Field(..., description="One-sentence root cause description")
    failure_stage: FailureStage = Field(..., description="Primary failure stage locus")
    failure_category: FailureCategory = Field(..., description="Primary failure category code")
    what_users_remember: List[str] = Field(default_factory=list, description="Commonly remembered clue types")
    what_users_forget: List[str] = Field(default_factory=list, description="Commonly forgotten metadata details")
    typical_search_behavior: str = Field(default="[Not Stated]", description="Typical user query / search strategy")
    typical_failure: str = Field(default="[Not Stated]", description="Root failure mode experienced by user")
    existing_workaround: str = Field(default="[Not Stated]", description="Existing workarounds used by users")
    evidence_ids: List[str] = Field(default_factory=list, description="List of evidence record IDs in cluster")
    evidence_count: int = Field(default=0, description="Total evidence count in cluster")
    unique_platforms: List[str] = Field(default_factory=list, description="Platforms where problem appears")
    frequency_rating: EvidenceStrength = Field(default=EvidenceStrength.MEDIUM, description="Frequency rating (High, Medium, Low)")
    severity_rating: EvidenceStrength = Field(default=EvidenceStrength.MEDIUM, description="Severity rating (High, Medium, Low)")
    confidence_rating: EvidenceStrength = Field(default=EvidenceStrength.MEDIUM, description="Evidence confidence rating (High, Medium, Low)")
    ai_relevance: str = Field(default="High", description="AI capability relevance assessment")
    technical_feasibility: str = Field(default="Medium", description="Technical feasibility assessment")
    important_unknowns: str = Field(default="Requires primary interview validation", description="Key research unknowns")


class OpportunityMatrixRow(BaseModel):
    cluster_id: str
    problem_name: str
    frequency: str
    severity: str
    evidence_strength: str
    ai_relevance: str
    feasibility: str
    key_tradeoff_note: str


class OpportunityMatrix(BaseModel):
    rows: List[OpportunityMatrixRow] = Field(default_factory=list)
