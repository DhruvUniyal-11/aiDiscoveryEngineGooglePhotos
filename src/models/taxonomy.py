"""
Taxonomy Enums and Definitions for Product Discovery & User Research Engine.
Adheres strictly to prd.md and research-brief.md definitions.
"""

from enum import Enum, IntEnum


class FailureStage(IntEnum):
    STAGE_1 = 1  # User Cannot Express the Memory (Expression Gap)
    STAGE_2 = 2  # System Cannot Understand the Expressed Memory (Intent Mapping Gap)
    STAGE_3 = 3  # System Understands but Retrieves Poor Candidates (Ranking & Recall Gap)
    STAGE_4 = 4  # Relevant Candidates Exist but Are Hard to Evaluate (Recognition & UI Gap)
    STAGE_5 = 5  # User Cannot Effectively Refine a Bad First Query (Refinement Gap)
    STAGE_6 = 6  # User Abandons Before Resolving (Abandonment Locus)
    STAGE_7 = 7  # Other (Unpredicted Failure Loci)

    def describe(self) -> str:
        descriptions = {
            1: "Stage 1: User Cannot Express the Memory (Expression Gap)",
            2: "Stage 2: System Cannot Understand the Expressed Memory (Intent Mapping Gap)",
            3: "Stage 3: System Understands but Retrieves Poor Candidates (Ranking & Recall Gap)",
            4: "Stage 4: Relevant Candidates Exist but Are Hard to Evaluate (Recognition & UI Gap)",
            5: "Stage 5: User Cannot Effectively Refine a Bad First Query (Refinement Gap)",
            6: "Stage 6: User Abandons Before Resolving (Abandonment Locus)",
            7: "Stage 7: Other (Unpredicted Failure Loci)",
        }
        return descriptions[self.value]


class FailureCategory(str, Enum):
    A = "A"  # Memory / Recall Problem
    B = "B"  # Query Expression Problem
    C = "C"  # System Understanding Problem
    D = "D"  # Retrieval / Ranking Problem
    E = "E"  # Result Evaluation Problem
    F = "F"  # Search Refinement Problem
    G = "G"  # Temporal Uncertainty
    H = "H"  # Location Uncertainty
    I = "I"  # Context / Event Memory Problem
    J = "J"  # Relationship / People Memory Problem
    K = "K"  # Visual Memory Problem
    L = "L"  # Text / Document Memory Problem

    def describe(self) -> str:
        descriptions = {
            "A": "A. Memory / Recall Problem",
            "B": "B. Query Expression Problem",
            "C": "C. System Understanding Problem",
            "D": "D. Retrieval / Ranking Problem",
            "E": "E. Result Evaluation Problem",
            "F": "F. Search Refinement Problem",
            "G": "G. Temporal Uncertainty",
            "H": "H. Location Uncertainty",
            "I": "I. Context / Event Memory Problem",
            "J": "J. Relationship / People Memory Problem",
            "K": "K. Visual Memory Problem",
            "L": "L. Text / Document Memory Problem",
        }
        return descriptions[self.value]


class MemoryClueType(IntEnum):
    PEOPLE = 1
    PLACE = 2
    TIME = 3
    EVENT = 4
    OBJECT = 5
    VISUAL = 6
    TEXT = 7
    NARRATIVE = 8
    EMOTION = 9

    def describe(self) -> str:
        descriptions = {
            1: "1. People / Relationships",
            2: "2. Place / Location",
            3: "3. Time / Temporal",
            4: "4. Event / Activity",
            5: "5. Object / Item",
            6: "6. Visual Appearance",
            7: "7. Text / OCR",
            8: "8. Narrative / Story",
            9: "9. Emotion / Mood",
        }
        return descriptions[self.value]


class PhotoEventuallyFound(str, Enum):
    YES = "Yes"
    NO = "No"
    PARTIAL = "Partial"
    ABANDONED = "Abandoned"


class EvidenceStrength(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ClaimTag(str, Enum):
    OBSERVED = "[Observed]"
    INFERRED = "[Inferred]"
    HYPOTHESIS = "[Hypothesis]"
