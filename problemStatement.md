# Problem Statement: Vague-Memory Photo Retrieval in Google Photos

**Team:** Core Experience, Google Photos
**Owner:** Dhruv (PM)
**Status:** Discovery — Pre-interview
**Last updated:** 22 Sept 2026

---

## 1. Background

Google Photos users accumulate thousands of photos, videos, screenshots, receipts, and scanned documents over years of use. Search works reasonably well when a user can state what they want precisely ("photos of my dog," "photos from Goa," "December 2025"). It breaks down when the user's memory of the photo is **fragmentary** — they remember *that* something happened, but not enough specific, searchable detail to retrieve it.

Example vague memories:
- "That small café we went to during our Goa trip."
- "The photo of the medicine I took when I was sick last year."
- "My friend's birthday, we were sitting outside."
- "The screenshot of a train ticket I booked months ago."

Users may retain fragments — people, location, event, activity, visual appearance, emotion, approximate sequence — while forgetting the fragments that search systems rely on: exact dates, place names, person names, albums, filenames, or exact text.

This is a **retrieval problem born of incomplete human memory**, not simply a "search is bad" problem — and that distinction matters for what gets built.

---

## 2. Problem Statement

> **Users who remember a photo only partially — by feeling, fragment, or story rather than precise metadata — frequently fail to retrieve it, and Google Photos currently offers no reliable way to recover a memory from incomplete recall.**

We do not yet know:
- Which stage of the retrieval funnel (expression → system understanding → candidate retrieval → evaluation → refinement) most often causes failure.
- Which categories of forgotten information are most common and most retrieval-blocking.
- Which user segments are most affected and how large/valuable those segments are.
- Whether the fix is about search *quality*, search *interaction model*, or something upstream (e.g. passive memory indexing).

This document exists to scope a **research phase**, not to justify a pre-chosen solution (e.g., conversational AI search). The research must let evidence — not assumption — determine where the real opportunity is.

---

## 3. Business Objective (North Star for this research)

**Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe, from the moment they begin searching.**

Working proxy metrics to validate/refine during research:
- Search-to-tap success rate on ambiguous/low-specificity queries
- Query reformulation count before success or abandonment
- Abandonment rate after a search session with no successful open
- (Qualitative) user-reported frustration/giving-up behavior

---

## 4. Core Research Question

**Why do users fail to retrieve old or vaguely remembered photos, even when they retain some memory of the photo — and at which stage does that failure actually occur?**

This is *not* simply "is Google Photos search hard to use." The research must localize failure to a specific stage:

| # | Failure locus | Question it answers |
|---|---|---|
| 1 | User cannot express the memory | Can they even form words for what they remember? |
| 2 | System cannot understand the expressed memory | Did the query fail to map to intent? |
| 3 | System understands but retrieves poor candidates | Is this a ranking/recall problem? |
| 4 | Relevant candidates exist but are hard to evaluate | Is this a results-UI / recognition problem? |
| 5 | User cannot effectively refine a bad first query | Is this a lack-of-refinement-tools problem? |
| 6 | User abandons before resolving | What causes give-up, and at what point? |
| 7 | Other | Reserved for patterns the taxonomy doesn't predict |

---

## 5. Scope

**In scope**
- Public, user-generated evidence (App Store/Play Store reviews, Reddit, Google Photos Help Community, YouTube comments, forums, social media) describing real retrieval attempts and failures.
- Both failed *and* successful vague-memory retrievals (success cases reveal what already works).
- Classification of failures against a retrieval-stage taxonomy and a memory-clue taxonomy.
- Segment-level pattern discovery (who is affected, and how).
- Adjacent/competitive retrieval behavior (Google Lens, Apple Photos, manual browsing, etc.) *only* as it relates to this specific problem.

**Out of scope (for this phase)**
- Proposing or evaluating a specific solution/MVP (e.g., conversational search, semantic search). That decision comes after evidence + interviews.
- Private/authenticated data sources.
- General Google Photos sentiment/UX research unrelated to memory-based retrieval.
- Primary user interviews (this phase informs their design; it doesn't replace them).

---

## 6. Research Method (summary)

1. **Evidence collection** — structured extraction from public sources using a defined field schema (source, quote, what's remembered/forgotten, query attempted, outcome, failure stage, category, confidence, etc.). No fabricated quotes, URLs, or statistics.
2. **Retrieval failure taxonomy** — classify each case into failure-stage and problem-type categories (memory/recall, query expression, system understanding, retrieval/ranking, result evaluation, refinement, temporal/location/relationship/visual/text uncertainty), extending the taxonomy where evidence demands it.
3. **Memory clue taxonomy** — catalog what people *do* naturally remember (people, place, time, event, object, visual appearance, text, narrative, emotion) versus what they forget, and whether current search can use each clue type.
4. **Journey mapping** — reconstruct representative retrieval journeys (memory → query → result → next action → outcome) rather than isolated complaints.
5. **Problem clustering** — group evidence into distinct, named retrieval problems with frequency, severity, and confidence ratings — explicitly avoiding a forced "winner."
6. **Business metric decomposition** — map failure stages onto the retrieval funnel and identify where the evidence concentrates.
7. **Hypothesis generation** — produce falsifiable, evidence-backed hypotheses to carry into user interviews (not the MVP itself).

Full field schemas, taxonomies, and output section structure are maintained in the companion research brief (see `research-brief.md` / prior working prompt) — this document is the scoping and framing layer above it.

---

## 7. Research Quality Rules (non-negotiable)

- Never fabricate sources, quotes, statistics, or user behavior.
- Distinguish **direct user evidence** from **researcher interpretation**.
- Distinguish **frequency** from **severity** — do not conflate them.
- Deduplicate repeated discussions of the same underlying incident.
- Label every finding's confidence: **High** (multiple independent sources), **Medium** (several relevant examples, limited breadth), **Low** (interesting but thin signal).
- Label every claim: **Observed** (user stated it), **Inferred** (reasonable read of behavior), or **Hypothesis** (needs validation).
- If evidence is insufficient to support a conclusion, say so explicitly rather than filling the gap.

---

## 8. Deliverables of This Research Phase

1. **Executive summary** of strongest findings (not a recommendation).
2. **Evidence table** with full field schema and confidence ratings.
3. **Retrieval failure taxonomy** with supporting evidence per category.
4. **Memory clue taxonomy** — what's remembered vs. forgotten, by frequency and retrieval implication.
5. **5–10 representative retrieval journeys.**
6. **Business metric decomposition** across the retrieval funnel.
7. **Opportunity comparison matrix** (frequency, severity, evidence strength, AI relevance, feasibility) — trade-offs shown, no winner declared.
8. **Evidence-backed user segments** and their retrieval scenarios.
9. **AI opportunity map** — candidate AI capabilities mapped to specific problems, with risks and supporting evidence (not a chosen solution).
10. **Research gaps** — what public data cannot tell us.
11. **8–12 falsifiable interview hypotheses**, each with a falsification condition, an interview question, and a behavioral task.
12. **Recommended next-phase research design** (participant profile, sample size, interview structure, tasks to observe).
13. **PM takeaways** — known, believed, uncertain, and what to validate next.

---

## 9. Definition of Done for This Phase

This research phase is complete when Dhruv can answer, with evidence and confidence levels attached:
- Where in the retrieval funnel do failures concentrate?
- What are the 3–6 most evidence-backed, distinct retrieval problems (not just complaints)?
- Which 1–2 problems are strong enough, in evidence and business relevance, to justify spending 5–6 real user interviews validating them?
- What specific, falsifiable hypotheses should those interviews test?

**Explicitly not done:** picking a feature, writing a PRD, or designing an MVP. That follows validation, not precedes it.

---

## 10. Key Risks / Open Questions

- **Evidence sparsity**: public reviews/forums may under-represent *successful* vague-memory retrieval (people don't post when things work) — may bias findings toward failure-only patterns.
- **Platform bias**: Reddit/forum users may skew toward power users with unusually large libraries, not representative of the mainstream user base.
- **Attribution risk**: a single vivid Reddit thread could be over-weighted relative to its actual frequency — confidence labeling exists specifically to guard against this.
- **Solution creep**: repeated exposure to "AI search" framing in source material could bias problem framing toward that solution prematurely — taxonomy and stage-labeling exist to guard against this.

---

## 11. Next Step

Proceed to evidence collection and classification per the research method above, culminating in the Section 1–14 output structure, ending with a **"What I Should Do Next"** section scoping the 5–6 person interview study.
