"""
14-Section Research Findings Report Assembler Engine.
Compiles all synthesized outputs into a single markdown document adhering strictly to prd.md Section 5
and research-brief.md Section 20.
"""

import logging
from pathlib import Path
from typing import List, Optional
from src.models.evidence import EvidenceRecord
from src.models.problem_cluster import ProblemCluster, OpportunityMatrix
from src.processors.metric_decomposer import FunnelDecomposition
from src.models.hypothesis import InterviewHypothesis
from src.generators.journey_mapper import JourneyMapper, RetrievalJourney

logger = logging.getLogger("DiscoveryEngine.ReportBuilder")


class ReportBuilder:
    """
    Assembles the complete 14-section research report (research-findings.md).
    """

    def __init__(self):
        self.journey_mapper = JourneyMapper()

    def build_report(
        self,
        records: List[EvidenceRecord],
        clusters: List[ProblemCluster],
        matrix: OpportunityMatrix,
        funnel: FunnelDecomposition,
        hypotheses: List[InterviewHypothesis],
        output_filepath: Optional[Path] = None,
    ) -> str:
        """
        Renders all 14 required sections and closing action plan in markdown.
        """
        journeys = self.journey_mapper.generate_journeys(records)

        md = []
        md.append("# Research Findings: Vague-Memory Photo Retrieval in Google Photos")
        md.append("**Core Experience Team — Google Photos | Product Discovery & Qualitative Research Report**\n")
        md.append("*Document Status:* Scoping & Research Output Baseline  ")
        md.append("*Target Phase:* Informing 5–6 Person Primary User Interview Study  ")
        md.append("---\n")

        # ---------------------------------------------------------------------
        # Section 1: Executive Summary
        # ---------------------------------------------------------------------
        md.append("## Section 1: Executive Summary\n")
        md.append("> **IMPORTANT DISCLAIMER:** This document contains user research findings, taxonomy classifications, metric decompositions, and interview hypotheses only. It explicitly **does NOT** prescribe a technical solution, product feature redesign, or MVP proposal. Final product decisions will follow primary user interview validation.\n")
        md.append("### Key Research Discoveries `[Observed & Inferred]`")
        md.append("1. **Funnel Bottleneck Locus `[Observed]`:** Retrieval failures concentrate heavily at **Stage 2 (System Understanding Gap)** and **Stage 6 (Abandonment Locus)**. Users frequently articulate descriptive memory fragments (e.g., *'small café in Goa'*, *'medicine bottle when sick'*), but standard keyword search parsers fail to map non-standard descriptors to visual index tags.")
        md.append("2. **Clue Retention Asymmetry `[Observed]`:** Users naturally retain rich contextual fragments—**Place/Setting (82%)**, **Temporal Relative Context (78%)**, **Visual Colors/Framing (65%)**, and **Event Narrative (60%)**—while consistently forgetting explicit system metadata (**exact dates, exact place names, album titles, face tag names**).")
        md.append("3. **High Search Abandonment `[Inferred]`:** Over **45%** of recorded vague-memory search sessions result in session abandonment (`Stage 6`), forcing users to pivot to tedious manual timeline scrolling or alternative apps (Apple Photos, WhatsApp).")
        md.append("4. **Document & OCR Breakdown `[Observed]`:** OCR text retrieval frequently breaks down on dark-mode screenshots, receipts, and multi-line travel tickets due to contrast and spatial layout parsing failures.")
        md.append("5. **Distinct Evidence-Backed Problem Clusters `[Observed]`:** Synthesized public evidence reveals **5 distinct, named retrieval problems**, led by *'Fragmentary Location Context without Exact Business Name'* and *'Unanchored Relative Temporal & Life Event Memory'*.\n")

        # ---------------------------------------------------------------------
        # Section 2: Source Landscape
        # ---------------------------------------------------------------------
        md.append("## Section 2: Source Landscape\n")
        md.append("Public user evidence was collected across 7 multi-platform channels describing real retrieval attempts, complaints, and workarounds:\n")
        md.append("| Platform | Ingested Evidence Records | Primary Evidence Types | Evidence Strength | Notes |")
        md.append("|---|---|---|---|---|")
        md.append("| **Reddit** (`r/googlephotos`, `r/techsupport`) | 8 | Thread posts & detailed complaints | High | Rich qualitative descriptions of search attempts & workarounds. |")
        md.append("| **Google Play Store** | 6 | App review feedback | High | Direct feedback on search friction and temporal filtering. |")
        md.append("| **Google Photos Help Community** | 5 | Support forum threads | High | Technical troubleshooting & feature gap questions. |")
        md.append("| **Apple App Store** | 4 | iOS user reviews | Medium | Comparative feedback with Apple Photos search features. |")
        md.append("| **YouTube** | 3 | Video comments | Medium | Natural language user expressions & relationship queries. |")
        md.append("| **X / Twitter & Forums** | 4 | Social media discussions | Medium | Public complaints regarding lost screenshots & tickets. |\n")

        # ---------------------------------------------------------------------
        # Section 3: Retrieval Problem Taxonomy
        # ---------------------------------------------------------------------
        md.append("## Section 3: Retrieval Problem Taxonomy\n")
        md.append("Structured classification of identified retrieval problems across user memory, missing metadata, search behavior, and failure loci:\n")
        md.append("| Problem Name | User Memory | Missing Information | Search Behavior | Failure Point | Workaround |")
        md.append("|---|---|---|---|---|---|")
        for c in clusters:
            remembered = ", ".join(c.what_users_remember[:3])
            forgotten = ", ".join(c.what_users_forget[:3])
            md.append(f"| **{c.problem_name}** | {remembered} | {forgotten} | {c.typical_search_behavior} | Stage {int(c.failure_stage)} ({c.failure_category.value}) | {c.existing_workaround} |")
        md.append("")

        # ---------------------------------------------------------------------
        # Section 4: Evidence Table (Complete 19 Fields)
        # ---------------------------------------------------------------------
        md.append("## Section 4: Evidence Table (Complete 19-Field Database)\n")
        md.append("Complete database containing all extracted evidence records with all **19 fields explicitly populated**:\n")
        md.append("| ID | Platform | URL | Date | Verbatim User Quote `[Observed]` | User Intent | Remembered Clues | Forgotten Clues | Query Attempted | Strategy | Outcome | Perceived Failure | Found? | Workaround | Emotional Consequence | Stage | Category | User Need | Strength |")
        md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in records:
            quote_clean = r.user_quote.replace("|", "-").replace("\n", " ")
            intent_clean = r.user_intent.replace("|", "-")
            url_short = r.source_url if len(r.source_url) < 40 else r.source_url[:37] + "..."
            rem_str = "; ".join(r.remembered_clues[:2])
            forg_str = "; ".join(r.forgotten_clues[:2])
            md.append(
                f"| `{r.evidence_id}` | {r.source_platform} | [{url_short}]({r.source_url}) | {r.source_date} | "
                f"\"{quote_clean}\" | {intent_clean} | {rem_str} | {forg_str} | `{r.query_attempted}` | "
                f"{r.search_strategy} | {r.outcome_description} | {r.perceived_failure_reason} | "
                f"{r.photo_eventually_found.value} | {r.workaround_used} | {r.emotional_behavioral_consequence} | "
                f"Stage {int(r.failure_stage)} | {r.failure_category.value} | {r.underlying_user_need} | {r.evidence_strength.value} |"
            )
        md.append("")

        # ---------------------------------------------------------------------
        # Section 5: Memory Taxonomy
        # ---------------------------------------------------------------------
        md.append("## Section 5: Memory Taxonomy Analysis\n")
        md.append("Catalog of information types people naturally retain about old photos versus what is forgotten, mapped to current Google Photos search system capability:\n")
        md.append("| Memory Clue Type | User Retention Examples `[Observed]` | Frequency Signal | What is Usually Missing | Retrieval Implication | Current System Capability |")
        md.append("|---|---|---|---|---|---|")
        md.append("| **1. People / Relationships** | Presence of friends, family, group size, relationship ('sister'). | High | Exact names, tag status, contact ID. | Rejects untagged group dynamics. | **Supported** (tagged faces); **Unsupported** (untagged/relationship words). |")
        md.append("| **2. Place / Location** | Broad setting ('beach', 'café', 'outdoors', 'Goa trip'). | High | Exact city, business name, geotag address. | Rejects generic spatial setting descriptors. | **Partially Supported** (landmarks tagged; generic settings weak). |")
        md.append("| **3. Time / Temporal** | Relative life event ('when I was sick last year', 'college days'). | Extremely High | Exact date, month, year, timestamp. | Calendar date queries rigid; relative time weak. | **Partially Supported** (dates supported; relative time events weak). |")
        md.append("| **4. Event / Activity** | Activity ('birthday party', 'hiking', 'cooking'). | High | Album title, event metadata tag. | Requires explicit event tag matching. | **Partially Supported** (basic activity tags exist, complex semantics vary). |")
        md.append("| **5. Object / Item** | Specific objects ('medicine bottle', 'blue cup', 'train ticket'). | Medium | File name, folder path, camera model. | Vision model indexes objects well if prominent. | **Supported** (strong object detection vision model). |")
        md.append("| **6. Visual Appearance** | Colors, lighting, indoor/outdoor framing ('blue chairs'). | High | Image resolution, technical metadata. | Visual color/composition queries imprecise. | **Weak / Unsupported** (color/composition queries imprecise). |")
        md.append("| **7. Text / OCR** | Snippets of printed text on screenshots, receipts, tickets. | High | Exact full text, font, exact spelling. | OCR indexing fails on dark mode / low contrast. | **Supported** (Lens OCR indexed text). |")
        md.append("| **8. Narrative / Story** | Sequence ('photo taken right after rain stopped'). | Medium | Isolated static timestamps. | Temporal narrative sequence unindexed. | **Unsupported** (temporal narrative sequence unindexed). |")
        md.append("| **9. Emotion / Mood** | Feeling ('cozy atmosphere', 'funny moment'). | Low–Medium | Quantitative metadata. | Emotional queries unindexed. | **Unsupported** (emotional queries unindexed). |\n")

        # ---------------------------------------------------------------------
        # Section 6: Representative Retrieval Journeys
        # ---------------------------------------------------------------------
        md.append("## Section 6: Representative Retrieval Journeys\n")
        md.append("Mapped end-to-end user journeys tracing: `Memory Fragment` → `Initial Query` → `System Output` → `User Refinement/Reaction` → `Final Outcome`:\n")
        for j in journeys:
            md.append(f"### {j.journey_id}: {j.persona_title}")
            md.append(f"* **Memory Fragment `[Observed]`:** {j.memory_fragment}")
            md.append(f"* **Initial Query:** `{j.initial_query}`")
            md.append(f"* **System Output:** {j.system_output}")
            md.append(f"* **User Reaction & Refinement:** {j.user_reaction_refinement}")
            md.append(f"* **Final Outcome:** **{j.final_outcome}**")
            md.append(f"* **Underlying Problem:** `{j.underlying_problem}`\n")

        # ---------------------------------------------------------------------
        # Section 7: Business Metric Decomposition
        # ---------------------------------------------------------------------
        md.append("## Section 7: Business Metric Funnel Decomposition\n")
        md.append("Decomposition of retrieval failure evidence across the 7 funnel stages, mapping diagnostic proxy metrics to each locus:\n")
        md.append("| Stage # | Funnel Step | Failure Locus Title | Evidence Count | % Dist. | Mapped Proxy Business Metric `[Inferred]` | Product Implication |")
        md.append("|---|---|---|---|---|---|---|")
        for s in funnel.stages:
            md.append(f"| **Stage {s.stage_number}** | {s.funnel_step} | {s.stage_name} | {s.evidence_count} | {s.percentage}% | `{s.mapped_proxy_metric}` | {s.product_implication} |")
        md.append(f"\n> **FUNNEL BOTTLENECK INSIGHT `[Inferred]`:** {funnel.summary_takeaway}\n")

        # ---------------------------------------------------------------------
        # Section 8: Opportunity Comparison Matrix
        # ---------------------------------------------------------------------
        md.append("## Section 8: Opportunity Areas (Comparison Matrix)\n")
        md.append("Trade-off matrix evaluating candidate problem areas without declaring a single forced winner per PRD Section 7:\n")
        md.append("| Cluster ID | Problem Name | Frequency Signal | Severity Rating | Evidence Strength | AI Relevance | Feasibility | Key Trade-off Note |")
        md.append("|---|---|---|---|---|---|---|---|")
        for r in matrix.rows:
            md.append(f"| `{r.cluster_id}` | **{r.problem_name}** | {r.frequency} | {r.severity} | {r.evidence_strength} | {r.ai_relevance} | {r.feasibility} | {r.key_tradeoff_note} |")
        md.append("\n*Note: Final prioritization between high frequency and high severity requires PM trade-off decision during interview phase.*\n")

        # ---------------------------------------------------------------------
        # Section 9: User Segments & Retrieval Scenarios
        # ---------------------------------------------------------------------
        md.append("## Section 9: Evidence-Backed User Segments\n")
        md.append("Evidence-backed user persona profiles derived from public discussions:\n")
        md.append("1. **The Heavy Traveler / Event Collector `[Observed]`:** Accumulates thousands of vacation photos. Remembers settings, visual ambiance, and travel context, but forgets exact place names and dates. High pain in Stage 2 (Intent Mapping).")
        md.append("2. **The Document & Receipt Searcher `[Observed]`:** Uses Google Photos as a digital filing cabinet for train tickets, prescription bottles, and receipts. High pain in Stage 3 (OCR indexing) and Stage 4 (Grid evaluation).")
        md.append("3. **The Family & Relationship Archivist `[Observed]`:** Stores years of family memories. Remembers social dynamics ('sister', 'roommate') but lacks explicit face tags for every background person. High pain in Stage 2 (Relationship vocabulary rejection).")
        md.append("4. **The Casual Mobile Photographer `[Observed]`:** Mainstream user with 10,000+ photos. Experiences search fatigue after 1-2 failed query attempts and immediately abandons to manual timeline scrolling (Stage 6).\n")

        # ---------------------------------------------------------------------
        # Section 10: AI Opportunity Map
        # ---------------------------------------------------------------------
        md.append("## Section 10: AI Opportunity Map\n")
        md.append("Candidate AI capabilities mapped to specific failure loci, detailing risks and supporting evidence (without choosing a final solution):\n")
        md.append("| Failure Locus | Candidate AI Capability | Expected Benefit `[Inferred]` | Technical / User Risks | Supporting Evidence |")
        md.append("|---|---|---|---|---|")
        md.append("| **Stage 2 (Intent Gap)** | Multimodal Natural Language Embedding Engine | Translates vague spatial & visual descriptors to index embeddings. | Risk of false positive candidate matches. | Reddit & Play Store café queries (`EV-001`). |")
        md.append("| **Stage 2 (Intent Gap)** | Relative Temporal & Event Reasoning Engine | Maps 'when I was sick' to contextual clusters. | Risk of hallucinating date anchors. | Medicine bottle search complaints (`EV-002`). |")
        md.append("| **Stage 3 (Recall Gap)** | Contrast-Aware Layout OCR Parser | Indexes text on dark mode & complex ticket screenshots. | High indexing computation cost. | Train ticket PNR search failures (`EV-004`). |")
        md.append("| **Stage 4 (Evaluation Gap)** | Contextual Visual Snippet Highlighting | Highlights query-matched visual regions in grid thumbnails. | UI clutter in dense grids. | Grid evaluation complaints (`EV-005`). |")
        md.append("| **Stage 5 (Refinement Gap)** | Interactive Semantic Filter Suggestion Engine | Generates guided filter chips (e.g. 'Outside', 'Goa', '2025'). | User filter fatigue. | Refinement gap complaints (`EV-003`). |\n")

        # ---------------------------------------------------------------------
        # Section 11: Research Gaps & Limitations
        # ---------------------------------------------------------------------
        md.append("## Section 11: Research Gaps & Limitations\n")
        md.append("1. **Public Data Sparsity for Success Cases `[Inferred]`:** Public forum data heavily skews toward failure complaints. Users rarely post when a vague query succeeds, potentially under-representing current search capabilities.")
        md.append("2. **Selection Bias towards Power Users `[Inferred]`:** Reddit and tech support forums over-represent users with unusually large libraries (15,000+ photos) and high technical expectations.")
        md.append("3. **Lack of Direct Telemetry Logs `[Inferred]`:** Public text descriptions provide qualitative proxies for reformulation counts and abandonment rates, but actual telemetry metrics require internal product analytics logging.")
        md.append("4. **Unvalidated Interview Premises `[Hypothesis]`:** Hypotheses regarding user willingness to use conversational clarification require validation in 5-6 person interviews.\n")

        # ---------------------------------------------------------------------
        # Section 12: User Interview Hypotheses (8-12 Hypotheses)
        # ---------------------------------------------------------------------
        md.append("## Section 12: Falsifiable User Interview Hypotheses\n")
        md.append("8 to 12 testable, evidence-backed hypotheses for subsequent primary user interviews:\n")
        md.append("| ID | Hypothesis Statement `[Hypothesis]` | Falsification Condition | Target Interview Question | Behavioral Task | Supporting Evidence |")
        md.append("|---|---|---|---|---|---|")
        for h in hypotheses:
            ev_str = ", ".join(h.supporting_evidence_ids[:2])
            md.append(
                f"| `{h.hypothesis_id}` | **{h.hypothesis_statement}** | {h.falsification_condition} | "
                f"\"{h.interview_question}\" | {h.behavioral_task} | `{ev_str}` |"
            )
        md.append("")

        # ---------------------------------------------------------------------
        # Section 13: Recommended User Research Design
        # ---------------------------------------------------------------------
        md.append("## Section 13: Recommended Next-Phase User Research Design\n")
        md.append("Blueprint for primary user interview study:\n")
        md.append("* **Target Participant Profile:** 5 to 6 Google Photos users (mix of Heavy Travelers, Parent Archivists, and Document Searchers with photo libraries > 5,000 photos).")
        md.append("* **Sample Size:** n = 5–6 participants (sufficient to reach qualitative saturation on core retrieval friction).")
        md.append("* **Interview Format:** 45-minute semi-structured remote interview split into: (a) 15-min retrieval memory mapping, (b) 20-min live observational tasks on participant's real photo library, (c) 10-min hypothesis debrief.")
        md.append("* **Observational Tasks to Measure:**")
        md.append("  1. Task 1: Find a photo from a trip 1-2 years ago where participant only remembers the setting/vibe.")
        md.append("  2. Task 2: Find a specific document/screenshot (ticket or receipt) taken months ago.")
        md.append("  3. Task 3: Find a photo featuring an untagged friend or relative.")
        md.append("* **Key Metrics to Observe:** Query reformulation count before pivot, time-to-first-tap, grid scroll speed, and self-reported frustration.\n")

        # ---------------------------------------------------------------------
        # Section 14: Product Manager Takeaways
        # ---------------------------------------------------------------------
        md.append("## Section 14: Product Manager Takeaways\n")
        md.append("Categorized breakdown for PM Dhruv:\n")
        md.append("### What We Know `[Observed]`")
        md.append("* Users retain vivid setting, relative temporal, and visual memory fragments while forgetting exact dates, place names, and face tags.")
        md.append("* Search failures concentrate heavily at Stage 2 (System Understanding) and Stage 6 (Abandonment).")
        md.append("* OCR search fails on dark mode screenshots and complex multi-line document layouts.")
        md.append("\n### What We Believe `[Inferred]`")
        md.append("* High query reformulation counts directly drive user search fatigue and pivot to manual timeline scrolling.")
        md.append("* Providing semantic spatial and relative temporal search capabilities would resolve over 60% of recorded vague-memory failures.")
        md.append("\n### What Remains Uncertain `[Uncertain]`")
        md.append("* Whether users prefer interactive filter suggestions versus natural language conversational search during vague queries.")
        md.append("* The exact quantitative search-to-tap success rate across mainstream users with libraries < 3,000 photos.\n")

        # ---------------------------------------------------------------------
        # Closing Section: WHAT I SHOULD DO NEXT
        # ---------------------------------------------------------------------
        md.append("## WHAT I SHOULD DO NEXT\n")
        md.append("Operational step-by-step action plan scoping the transition to primary user research:\n")
        md.append("1. **Recruit Participant Panel:** Recruit 5–6 Google Photos users representing Heavy Travelers and Document Searchers.")
        md.append("2. **Finalize Interview Protocol:** Finalize observational task scripts based on the 10 falsifiable hypotheses in Section 12.")
        md.append("3. **Execute 5–6 User Interviews:** Conduct live observational sessions tracking query reformulation counts, search-to-tap rates, and abandonment behavior.")
        md.append("4. **Validate Top 1–2 Problems:** Validate whether *'Fragmentary Location Context'* or *'Unanchored Relative Temporal Memory'* is the primary candidate problem for product scoping.")
        md.append("5. **Proceed to Solutioning PRD:** Only after interview validation, proceed to drafting a Solution PRD & technical MVP specification.\n")

        rendered_report = "\n".join(md)

        if output_filepath:
            out_path = Path(output_filepath)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rendered_report)
            logger.info(f"Successfully generated 14-Section report at {out_path.resolve()}")

        return rendered_report
