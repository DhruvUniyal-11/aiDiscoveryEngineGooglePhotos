# Product Requirements Document (PRD)
## Product Discovery & User Research Engine for Vague-Memory Photo Retrieval

**Target Domain:** Google Photos Core Experience — Vague-Memory Retrieval Research  
**Document Owner:** Dhruv (PM)  
**Status:** Scoping & Requirements Baseline (Updated with `research-brief.md`)  
**Target Output Artifact:** `research-findings.md` (14-Section Structured Research Report)  
**Reference Inputs:** [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md) & [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md)

---

## 1. Purpose & Non-Goals

### 1.1 Purpose
The **Product Discovery & User Research Engine** is an automated research synthesis and intelligence system designed to collect, extract, classify, cluster, and report on public user evidence regarding vague-memory photo retrieval failures. 

When users accumulate thousands of personal media files (photos, videos, screenshots, receipts, tickets, scanned documents), exact keyword/metadata search breaks down if their memory is fragmentary (remembering feelings, visual cues, or narratives rather than place names, dates, or file titles). This engine automates the evidence-gathering and qualitative-analysis pipeline to discover where in the retrieval funnel failures concentrate, identify distinct evidence-backed retrieval problems, decompose business metrics, and generate falsifiable hypotheses for primary user interviews.

### 1.2 Non-Goals (Hard Constraints)
* **NO Solutioning:** The engine MUST NOT propose, design, evaluate, or recommend specific technical or product solutions (e.g., conversational AI search, vector search engines, UI redesigns, filter chips).
* **NO MVP Proposals:** The engine MUST NOT define minimum viable products, feature specifications, or product roadmaps.
* **Research Output Only:** The engine's sole purpose is to produce rigorous, structured research output (`research-findings.md`), taxonomies, journey maps, and interview hypotheses.
* **NO Private/Authenticated Data Processing:** The engine operates strictly on public, unauthenticated, user-generated data sources (reviews, forums, public comments). It MUST NOT access private Google Photos user libraries, internal telemetry logs, or personal user data.
* **NO Primary Interview Execution:** The engine does not conduct live user interviews; it synthesizes public evidence to *design* the structure, tasks, and hypotheses for subsequent primary user interviews.
* **NO Generic Sentiment Scraping:** The engine MUST NOT process general app complaints (e.g., storage pricing, backup battery drain, app crashes) that are unrelated to vague-memory photo retrieval.

---

## 2. Functional Requirements

### FR-1: Evidence Collection & Source Ingestion
* **FR-1.1:** System MUST ingest public, user-generated content from multi-platform public sources:
  * Google Play Store reviews
  * Apple App Store reviews
  * Reddit (e.g., `r/googlephotos`, `r/techsupport`, `r/apps`)
  * Google Photos Help Community forums
  * YouTube video comments discussing photo management/retrieval
  * X/Twitter and other social media, public technology forums, blog comments
* **FR-1.2:** System MUST capture both **failure cases** (unsuccessful retrieval attempts) and **success cases** (successful retrieval attempts using workaround strategies or specific clues).

### FR-2: Structured Evidence Extraction
* **FR-2.1:** System MUST parse raw user statements into structured evidence records adhering strictly to the **19-Field Evidence Record Schema** (Section 3).
* **FR-2.2:** System MUST enforce the Zero-Fabrication requirement during extraction — quotes, URLs, and queries must be verbatim or explicitly tagged as researcher interpretations.

### FR-3: Taxonomy Classification
* **FR-3.1 Retrieval Failure Classification:** System MUST classify every evidence record against the Retrieval-Failure Taxonomy (Categories A–L & Funnel Stages 1–7; Section 4.1).
* **FR-3.2 Memory Clue Classification:** System MUST map remembered information elements against the Memory-Clue Taxonomy (Section 4.2) and catalog forgotten details (Section 4.3).

### FR-4: Problem Clustering & Pattern Discovery
* **FR-4.1:** System MUST cluster related evidence records into distinct, named retrieval problems (e.g., "Fragmentary Event Context without Temporal Anchor").
* **FR-4.2:** System MUST calculate aggregate Frequency, Severity, and Confidence labels for each identified problem cluster without declaring a single forced "winning" problem.

### FR-5: Business Metric Funnel Decomposition
* **FR-5.1:** System MUST map classified failure stages onto the standard retrieval funnel (`User Memory` → `Ability to Express` → `System Understanding` → `Candidate Retrieval` → `Result Evaluation` → `Search Refinement` → `Outcome`).
* **FR-5.2:** System MUST correlate failure stages with working proxy business metrics:
  * Search-to-tap success rate on ambiguous queries
  * Query reformulation count per session
  * Abandonment rate following empty/irrelevant result sets

### FR-6: Falsifiable Hypothesis Generation
* **FR-6.1:** System MUST produce 8–12 structured, evidence-backed hypotheses for subsequent primary user interviews.
* **FR-6.2:** Each hypothesis MUST contain: (a) Hypothesis Statement, (b) Evidence Supporting It, (c) Falsification Condition, (d) Target Interview Question, and (e) Observational Behavioral Task.

### FR-7: Standardized Report Generation
* **FR-7.1:** System MUST compile all synthesized findings into a single, fully structured Markdown document adhering exactly to the **14-Section `research-findings.md` Output Specification** (Section 5).

---

## 3. Full Evidence Record Schema (All 19 Fields)

Every ingested evidence record MUST populate all 19 fields explicitly as specified in Section 6 of [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md#L56-L79). No fields may be dropped, summarized, or omitted.

| Field # | Field Name | Data Type | Description & Valid Values |
|---|---|---|---|
| **1** | `source_platform` | Enum | Platform where evidence originated: `[Play Store, App Store, Reddit, Google Help Community, YouTube, X/Twitter, Forum, Blog]` |
| **2** | `source_url` | URI / String | Canonical link to the specific public post, review, or comment thread. MUST NOT be fabricated. |
| **3** | `source_date` | Date / String | Date of publication/posting, if available (or `[Not Stated]`). |
| **4** | `user_quote` | String | Direct, verbatim user quote or close paraphrase detailing the retrieval attempt. MUST NOT be fabricated. |
| **5** | `user_intent` | String | Concise description of what the user was trying to find. |
| **6** | `remembered_clues` | Array[String] | Specific details or clues the user remembered (e.g., `["location: café", "event: Goa trip"]`). |
| **7** | `forgotten_clues` | Array[String] | Crucial metadata or details the user explicitly forgot (e.g., `["exact date", "place name"]`). |
| **8** | `query_attempted` | String | Exact search term(s) or query string(s) entered by the user (if stated/observable). |
| **9** | `search_strategy` | String | Search approach used (e.g., keyword combo, face filter, timeline scrolling, Lens). |
| **10** | `outcome_description` | String | Description of what happened during/after search execution. |
| **11** | `perceived_failure_reason` | String | Why the user believes retrieval failed (user's perspective). |
| **12** | `photo_eventually_found` | Enum | Final retrieval status: `[Yes, No, Partial, Abandoned]`. |
| **13** | `workaround_used` | String | Workaround strategy used by user (e.g., manual scroll, ask friend, check WhatsApp, Lens). |
| **14** | `emotional_behavioral_consequence` | String | Explicitly stated user reaction (e.g., frustration, giving up, app deletion threat). |
| **15** | `failure_stage` | Enum | Stage of failure in funnel: `[Stage 1: Cannot Express, Stage 2: System Cannot Understand, Stage 3: Poor Candidates, Stage 4: Evaluation Hard, Stage 5: Refinement Hard, Stage 6: Abandonment, Stage 7: Other]`. |
| **16** | `failure_category` | Enum | Primary taxonomy category: `[A. Memory/Recall, B. Query Expression, C. System Understanding, D. Retrieval/Ranking, E. Result Evaluation, F. Search Refinement, G. Temporal Uncertainty, H. Location Uncertainty, I. Context/Event Memory, J. Relationship/People Memory, K. Visual Memory, L. Text/Document Memory]`. |
| **17** | `underlying_user_need` | String | Analytical synthesis of latent user requirement. |
| **18** | `evidence_strength` | Enum | Evidence quality/confidence rating: `[High (Multiple independent sources), Medium (Several examples, limited breadth), Low (Thin signal)]`. |
| **19** | `notes` | String | Additional researcher annotations, cross-references, or context. |

---

## 4. System Taxonomies

To ensure self-containment, the PRD restates the complete **Retrieval-Failure Taxonomy**, **Memory-Clue Taxonomy**, and **Forgotten Information Taxonomy** as detailed in [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md).

### 4.1 Retrieval-Failure Taxonomy

The retrieval funnel comprises 7 failure-type stage distinctions (1–7) and 12 core failure problem categories (A–L):

#### Funnel Failure-Type Stages (Assign to Every Case)
```
[User Memory / Intent] 
       │
       ▼
(1) User cannot express memory ────────────────► Cannot articulate searchable keywords
       │
       ▼
(2) System cannot understand memory ──────────► Query entered, parser misinterprets intent
       │
       ▼
(3) System understands but retrieves poor candidates ─► Ranking / recall failure
       │
       ▼
(4) Relevant candidates exist but hard to evaluate ────► Recognition / UI grid failure
       │
       ▼
(5) User cannot effectively refine search ─────► Dead-end search, no filter chips/suggestions
       │
       ▼
(6) User abandons search ──────────────────────► Gives up search session due to fatigue
       │
       ▼
(7) Other ────────────────────────────────────► Unpredicted failure pattern outside funnel
```

#### Core Problem Categories (A–L)
* **A. Memory / Recall Problem:** User remembers photo only through vague or incomplete memories ("I remember the café but not its name").
* **B. Query Expression Problem:** User has a memory but struggles to translate it into searchable language.
* **C. System Understanding Problem:** User provides meaningful clues, but the system fails to parse intended meaning.
* **D. Retrieval / Ranking Problem:** Relevant photo exists in library but is not surfaced effectively in results.
* **E. Result Evaluation Problem:** Relevant candidates present in grid, but user struggles to recognize or spot the correct item.
* **F. Search Refinement Problem:** User knows initial query is insufficient but lacks tools/guidance to narrow results.
* **G. Temporal Uncertainty:** User remembers approximate time/season, but not exact date or timestamp.
* **H. Location Uncertainty:** User remembers a general place/trip context, but not exact city or GPS location.
* **I. Context / Event Memory Problem:** User remembers a story, event, or situation rather than searchable metadata.
* **J. Relationship / People Memory Problem:** User remembers social dynamics ("me and my roommate") but not searchable tag names.
* **K. Visual Memory Problem:** User remembers visual properties ("blue wall", "sitting outside") but not exact semantic keywords.
* **L. Text / Document Memory Problem:** User remembers a screenshot/receipt/ticket, but not exact printed words for OCR search.

---

### 4.2 Memory-Clue Taxonomy

Analysis of information types people naturally retain about old photos:

| Clue Category | What Users Remember | Frequency in Evidence | Expressed Naturally? | Current Google Photos Search Capability |
|---|---|---|---|---|
| **1. People / Relationships** | Presence of friends, family, group size, relationship ("roommate"). | High | Yes | **Supported** (tagged faces); **Unsupported** (untagged/relationship dynamics). |
| **2. Location / Place** | Broad setting ("beach", "café", "trip to Goa"). | High | Yes | **Partially Supported** (cities/landmarks tagged; generic settings weak). |
| **3. Temporal / Time** | Relative time, season, life phase ("when I was sick last year"). | Extremely High | Yes | **Partially Supported** (dates/years supported; relative time events weak). |
| **4. Event / Activity** | Activity ("birthday party", "hiking", "cooking"). | High | Yes | **Partially Supported** (basic activity tags exist, complex semantics vary). |
| **5. Object / Item** | Specific scene items ("medicine bottle", "blue cup"). | Medium | Yes | **Supported** (vision object detection). |
| **6. Visual Appearance** | Colors, lighting, seating, indoor/outdoor context. | High | Yes | **Weak / Unsupported** (color/composition search imprecise). |
| **7. Text / OCR** | Fragments of text on documents, tickets, screenshots. | High | Yes | **Supported** (Lens OCR indexed text). |
| **8. Narrative / Story** | Event sequence ("photo taken right after rain stopped"). | Medium | Yes | **Unsupported** (narrative sequence unindexed). |
| **9. Emotion / Context** | Mood, feeling, tone ("cozy atmosphere", "funny moment"). | Low–Medium | Yes | **Unsupported** (emotional queries unindexed). |

---

### 4.3 Forgotten Information Taxonomy

Analysis of information users explicitly forget when searching:
* **Exact Date / Timestamp:** Users remember *what* happened, but forget *when*.
* **Exact Location / Business Name:** Users remember spatial context ("café"), but forget exact name or city.
* **Person's Name / Tag:** Users remember *who* was present, but forget exact tag or name.
* **Album / Folder / Filename:** Users rarely recall structural storage containers or system names.
* **Exact Printed Text:** Users remember having a receipt or ticket, but forget exact invoice numbers or text strings.
* **Camera / Device Details:** Users forget which device or app took the photo.

---

## 5. Output Specification: 14-Section `research-findings.md` Structure

The engine MUST output research findings in a single markdown document adhering to Section 20 of [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md#L205-L235):

```
research-findings.md
├── Section 1: Executive Summary
├── Section 2: Source Landscape
├── Section 3: Retrieval Problem Taxonomy
├── Section 4: Evidence Table (All 19 Schema Fields)
├── Section 5: Memory Taxonomy
├── Section 6: Retrieval Journeys (5–10 Journeys)
├── Section 7: Business Metric Decomposition
├── Section 8: Opportunity Areas (Opportunity Comparison Matrix)
├── Section 9: User Segments
├── Section 10: AI Opportunity Map
├── Section 11: Research Gaps
├── Section 12: User Interview Hypotheses (8–12 Hypotheses)
├── Section 13: Recommended User Research Design
└── Section 14: Product Manager Takeaways
    └── Closing: "WHAT I SHOULD DO NEXT" (Operational Action Plan)
```

### Detailed Section Requirements

* **Section 1: Executive Summary:** 5–8 strongest findings; top retrieval failure patterns, memory clues, forgotten info, search behaviors, and major opportunity areas. Explicit disclaimer: NO final solution recommendation.
* **Section 2: Source Landscape:** Tabular overview (`Platform | Number of sources | Evidence types | Strength | Notes`).
* **Section 3: Retrieval Problem Taxonomy:** Structured breakdown (`Problem | User memory | Missing info | Search behavior | Failure point | Workaround`).
* **Section 4: Evidence Table:** Complete tabular database containing all evidence records with all 19 schema fields populated.
* **Section 5: Memory Taxonomy:** Analysis table (`Memory type | Examples | Frequency signal | What is missing | Retrieval implication | Evidence`).
* **Section 6: Retrieval Journeys:** 5 to 10 mapped journeys tracing: `Memory` → `Search attempt` → `Result` → `Next action` → `Failure/Success` → `Underlying problem`.
* **Section 7: Business Metric Decomposition:** Funnel stages mapped to diagnostic proxy metrics and evidence concentrations.
* **Section 8: Opportunity Areas:** Trade-off matrix evaluating problems on: Frequency, Severity, Evidence Strength, AI Relevance, and Technical Feasibility. MUST NOT declare a single forced winner.
* **Section 9: User Segments:** Evidence-backed persona profiles paired with retrieval scenarios.
* **Section 10: AI Opportunity Map:** Mapping candidate AI capabilities to specific failure loci, detailing risks and supporting evidence without selecting a final solution.
* **Section 11: Research Gaps:** Analysis of public data limitations, selection bias, and unverified assumptions.
* **Section 12: User Interview Hypotheses:** 8 to 12 testable hypotheses (`Hypothesis | Supporting Evidence | Falsification Condition | Interview Question | Behavioral Task`).
* **Section 13: Recommended User Research Design:** Blueprint for follow-up primary user research (target profile, sample size n=5–6, interview protocol, tasks, observation metrics).
* **Section 14: Product Manager Takeaways:** Categorized breakdown (`What We Know`, `What We Believe`, `What Remains Uncertain`, `What Should Be Validated Next`).
* **Closing Section ("WHAT I SHOULD DO NEXT"):** Concrete, step-by-step next research actions required to validate top opportunities with 5–6 real users.

---

## 6. Research Quality Rules (Hard Requirements)

The engine MUST enforce the following rules (from Section 18 of [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md#L175-L192)) as **strict, non-negotiable system requirements**:

1. **Zero Fabrication (HARD REQUIREMENT):** NEVER generate, fake, simulate, or extrapolate user quotes, URLs, source references, or empirical statistics.
2. **Strict Claim Tagging (HARD REQUIREMENT):** Every claim MUST be tagged as `[Observed]` (direct user quote), `[Inferred]` (researcher deduction), or `[Hypothesis]` (unvalidated premise).
3. **Frequency vs. Severity Disambiguation (HARD REQUIREMENT):** Volume MUST NOT be conflated with impact. High-frequency minor issues and low-frequency severe issues MUST be evaluated separately.
4. **Mandatory Deduplication (HARD REQUIREMENT):** Repeated discussions of the same underlying post/incident across platforms MUST be merged into one record.
5. **Rigorous Confidence Labeling (HARD REQUIREMENT):** Every finding MUST be tagged as `High Confidence` (multiple independent sources), `Medium Confidence` (several examples, limited breadth), or `Low Confidence` (thin signal).
6. **Explicit Gap Reporting (HARD REQUIREMENT):** If evidence is weak or insufficient, the engine MUST explicitly state the gap in Section 11 rather than making conjectures.

---

## 7. Success Criteria & Definition of Done

Adopts the exact **Definition of Done** established in [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md#L133-L140) §9.

### 7.1 Success Criteria
The research phase executed by this engine is complete **ONLY** when PM Dhruv can answer the following four questions, backed by concrete evidence records and confidence ratings:

1. **Funnel Locus Concentration:** Where in the retrieval funnel (`Expression` → `Understanding` → `Candidate Retrieval` → `Evaluation` → `Refinement` → `Outcome`) do user failures most heavily concentrate?
2. **Distinct Evidence-Backed Problems:** What are the **3 to 6** most evidence-backed, distinct retrieval problems (root causes, not mere complaints)?
3. **Validation Candidates:** Which **1 to 2** problems possess sufficient evidence strength and business relevance to justify conducting 5–6 primary user interviews?
4. **Falsifiable Hypotheses:** What specific, falsifiable hypotheses should those 5–6 primary user interviews test?

### 7.2 Explicit "Not Done" Boundaries
The research phase is explicitly **NOT DONE** with:
* Picking a technical architecture or product feature.
* Writing a solution PRD or spec document.
* Designing an MVP, wireframe, or prototype.

---

## 8. Flagged Ambiguities & Discrepancy Resolution

Analysis of [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md) and [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md) reveals the following items requiring clear resolution:

> [!NOTE]
> **Resolution of Companion Document (`research-brief.md`)**  
> `research-brief.md` has been added to the workspace. Its 19-field schema, taxonomies, 14-section output structure, and 15 research quality rules are now fully integrated into `prd.md`.

| # | Item / Discrepancy | Details & Impact | Resolution in PRD |
|---|---|---|---|
| **A-1** | **Section Title & Order Minor Discrepancies** | [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md#L113-L128) §8 lists 13 deliverables, while [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md#L205-L235) §20 explicitly details 14 sections plus closing section. | PRD adopts the 14-section structure from `research-brief.md` §20 as the authoritative output spec. |
| **A-2** | **Qualitative Public Data vs. Quantitative Proxy Metrics** | Telemetry proxy metrics (search-to-tap rate, reformulation count, abandonment rate) are defined for internal app logs, but input data is qualitative public posts. | Engine must infer proxy metric trends qualitatively from user descriptions (e.g., "searched 10 times" = high reformulation count) and tag as `[Inferred]`. |
| **A-3** | **Unquantified Thresholds for Frequency & Severity** | Both documents require labeling Frequency and Severity (`High/Medium/Low`) without specifying exact numerical count thresholds. | Quantitative count thresholds (e.g., `High Frequency` = ≥10 independent sources) MUST be specified in the technical implementation plan. |
| **A-4** | **Lack of Objective Selection Algorithm for 1–2 Problems** | System must select 1–2 focus problems for interviews, but no explicit weighting formula is provided. | Implement a multi-criteria trade-off matrix in Section 8 of the report with explicit weighted scoring. |
| **A-5** | **Multi-Session / Cross-Platform Journey Disambiguation** | Public forum posts often blur multiple search attempts over weeks. | Define journey mapping rules: single post = 1 journey unless user explicitly notes distinct dates/episodes. |

---

## 9. Next Steps
1. Review updated [`prd.md`](file:///c:/project_cursor/ai_discoveryEngine/prd.md) for complete alignment with [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md) and [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md).
2. Proceed to technical design and Implementation Plan (`implementation_plan.md`) without jumping to product solutioning.
