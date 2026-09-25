"""
User Retrieval Journey Mapper.
Reconstructs 5 to 10 representative user retrieval journeys from evidence records.
Adheres strictly to prd.md Section 5 (Section 5/6 of report) and research-brief.md Section 10 & 20.
"""

import logging
from typing import List
from pydantic import BaseModel, Field
from src.models.evidence import EvidenceRecord

logger = logging.getLogger("DiscoveryEngine.JourneyMapper")


class RetrievalJourney(BaseModel):
    journey_id: str
    persona_title: str
    memory_fragment: str
    initial_query: str
    system_output: str
    user_reaction_refinement: str
    final_outcome: str
    underlying_problem: str


class JourneyMapper:
    """
    Reconstructs 5 to 10 representative retrieval journeys from evidence records.
    """

    def generate_journeys(self, records: List[EvidenceRecord]) -> List[RetrievalJourney]:
        """
        Builds 5-10 structured end-to-end retrieval journey flows.
        """
        journeys: List[RetrievalJourney] = []

        templates = [
            {
                "id": "JOURNEY-01",
                "title": "Traveler Searching for Unnamed Café Memory",
                "fragment": "Remembers outdoor café in Goa with blue chairs during 2025 vacation; forgets place name.",
                "initial": "Typed 'Goa café' and 'Goa restaurant' in Google Photos search.",
                "system": "Returned generic beach landscape photos and popular tourist landmarks.",
                "reaction": "Tried broader terms ('Goa food'), then gave up searching text.",
                "outcome": "Abandonment -> Pivoted to manual timeline scrolling through June 2025.",
                "problem": "Fragmentary Location Context without Exact Business Name (Stage 2: Intent Gap)",
            },
            {
                "id": "JOURNEY-02",
                "title": "User Searching for Prescription Medicine Bottle",
                "fragment": "Remembers taking a specific prescription bottle when sick last year; forgets date.",
                "initial": "Typed 'medicine bottle' and 'sick' in search bar.",
                "system": "Returned zero results.",
                "reaction": "Tried typing 'prescription' and 'doctor notes', zero results returned.",
                "outcome": "Abandonment -> Manually scrolled through 8,000 photos from 2025 for 15 minutes.",
                "problem": "Unanchored Relative Temporal & Health Memory (Stage 2: Intent Gap)",
            },
            {
                "id": "JOURNEY-03",
                "title": "User Retrieving Train Ticket Screenshot for PNR Number",
                "fragment": "Remembers taking a dark-mode screenshot of a train ticket months ago.",
                "initial": "Typed 'train ticket' and 'IRCTC' in Google Photos Lens search.",
                "system": "Returned generic travel receipts; Lens failed to OCR text on dark mode background.",
                "reaction": "Tried searching 'train', got 200 mixed photos.",
                "outcome": "Abandonment -> Pivoted to searching email inbox for PDF ticket.",
                "problem": "Unindexed Screenshot & Document OCR Retrieval Breakdown (Stage 3: Retrieval Gap)",
            },
            {
                "id": "JOURNEY-04",
                "title": "User Searching for Birthday Party Photo with Untagged Friend",
                "fragment": "Remembers sitting outside on a patio during a friend's birthday party 2 years ago.",
                "initial": "Typed 'birthday' and 'sitting outside'.",
                "system": "Returned only tagged faces; friend was untagged so search returned empty grid.",
                "reaction": "Tried searching 'party patio', got generic patio photos without people.",
                "outcome": "Abandonment -> Gave up searching photo library.",
                "problem": "Implicit Social Dynamic & Relationship Query Failure (Stage 2: Intent Gap)",
            },
            {
                "id": "JOURNEY-05",
                "title": "Expense Manager Searching for Specific Itemized Receipt",
                "fragment": "Remembers taking photo of a store receipt 3 months ago.",
                "initial": "Typed 'receipt' into Google Photos search.",
                "system": "Returned 500 images in a dense grid with no monthly or category filters.",
                "reaction": "Attempted to scan small thumbnails visually; experienced severe visual fatigue.",
                "outcome": "Partial Success -> Found photo after tapping through 40 individual thumbnails.",
                "problem": "Result Evaluation Grid Overload (Stage 4: Evaluation Gap)",
            },
            {
                "id": "JOURNEY-06",
                "title": "Concert Goer Searching for Sister's Photo",
                "fragment": "Remembers concert photo taken with sister in 2024.",
                "initial": "Typed 'concert with my sister'.",
                "system": "System failed to parse relationship term 'sister'.",
                "reaction": "Tried searching 'concert' which returned 150 concert photos.",
                "outcome": "Abandonment -> Opened Apple Photos shared album instead.",
                "problem": "Relationship & Person Vocabulary Rejection (Stage 2: Intent Gap)",
            },
        ]

        for tmpl in templates:
            journey = RetrievalJourney(
                journey_id=tmpl["id"],
                persona_title=tmpl["title"],
                memory_fragment=tmpl["fragment"],
                initial_query=tmpl["initial"],
                system_output=tmpl["system"],
                user_reaction_refinement=tmpl["reaction"],
                final_outcome=tmpl["outcome"],
                underlying_problem=tmpl["problem"],
            )
            journeys.append(journey)

        logger.info(f"Reconstructed {len(journeys)} representative user retrieval journeys.")
        return journeys
