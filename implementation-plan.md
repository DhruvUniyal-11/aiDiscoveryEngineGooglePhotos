# Implementation Plan: Product Discovery & User Research Engine

This document provides the technical implementation plan for building the **Product Discovery & User Research Engine** for Vague-Memory Photo Retrieval in Google Photos, based on [`prd.md`](file:///c:/project_cursor/ai_discoveryEngine/prd.md), [`problemStatement.md`](file:///c:/project_cursor/ai_discoveryEngine/problemStatement.md), and [`research-brief.md`](file:///c:/project_cursor/ai_discoveryEngine/research-brief.md).

---

## Technical Architecture & Technology Stack

### System Architecture Overview

The engine is designed as an autonomous, modular discovery pipeline that processes raw public user data into structured evidence records, classifies them against domain taxonomies, clusters retrieval problems, maps funnel business metrics, generates falsifiable hypotheses, and renders a 14-section markdown research report (`research-findings.md`).

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                            1. SOURCE INGESTION LAYER                              │
│   Play Store  │  App Store  │  Reddit  │  Google Help  │  YouTube  │  Social/Forums │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Raw Text Payloads
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        2. EXTRACTION & SCHEMA MAPPING LAYER                       │
│    LLM Extractor (Pydantic Schema) ──► 19-Field Evidence Record Store (JSONL/SQLite) │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Validated Records
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           3. DEDUPLICATION LAYER                                  │
│            Canonical URL Matching + Embedding Cosine Similarity Merger             │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Unique Evidence Records
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        4. TAXONOMY CLASSIFICATION LAYER                           │
│   7 Funnel Failure Stages (1-7)  │  12 Problem Categories (A-L)  │ Memory Clues (1-9)│
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Classified & Tagged Records
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                       5. CLUSTERING & METRIC FUNNEL LAYER                         │
│     Semantic Problem Clustering  │  Proxy Metric Funnel Mapping (Search-to-Tap)    │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Problem Clusters & Funnel Metrics
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     6. HYPOTHESIS GENERATION & REPORT ASSEMBLY                    │
│   8-12 Falsifiable Hypotheses  │  14-Section Report Builder (research-findings.md)  │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Full Report & Evidence Database
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          7. RESEARCH QUALITY QA VALIDATOR                         │
│     Zero Fabrication Check  │  Citation Resolver  │  Claim & Confidence Label QA  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Proposed Technology Stack
* **Language & Runtime:** Python 3.11+
* **Data Modeling & Validation:** `pydantic` v2 (strict type enforcement & JSON Schema generation)
* **LLM Orchestration & Extraction:** `google-genai` / `litellm` with Structured Outputs (JSON Mode)
* **Storage Layer:** `sqlite3` + `jsonlines` (zero-dependency, file-backed transactional store)
* **Text Similarity & Deduplication:** `scikit-learn` (TF-IDF / Cosine Similarity) & `rapidfuzz`
* **CLI & Pipeline Orchestration:** `click` / `typer` + `rich` (terminal formatting & progress indicators)
* **Testing Framework:** `pytest` + `pytest-asyncio`

---

## Proposed Project File Structure

```
ai_discoveryEngine/
├── config/
│   ├── default_config.yaml         # Default parameters, queries, and rate limits
│   └── taxonomy_rules.yaml         # Taxonomy category mappings & prompt guidelines
├── src/
│   ├── __init__.py
│   ├── config.py                   # Config loader & validation models
│   ├── models/
│   │   ├── __init__.py
│   │   ├── evidence.py             # 19-Field EvidenceRecord Pydantic model
│   │   ├── taxonomy.py             # Enums & structures for Failure Stages & Memory Clues
│   │   ├── problem_cluster.py      # Problem Cluster data structure
│   │   ├── hypothesis.py           # Falsifiable Hypothesis data model
│   │   └── report.py               # Report structure & section data models
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── repository.py           # SQLite & JSONL storage manager
│   │   └── exporter.py             # Export helpers (Markdown, CSV, JSON)
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract base collector class
│   │   ├── reddit_collector.py     # Reddit public post scraper/API adapter
│   │   ├── play_store_collector.py # Play Store review collector
│   │   ├── app_store_collector.py  # App Store review collector
│   │   ├── google_help_collector.py# Google Support community collector
│   │   ├── youtube_collector.py    # YouTube comment thread collector
│   │   └── forum_collector.py      # Generic web forum collector
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── extractor.py            # LLM 19-field schema extractor
│   │   ├── deduplicator.py         # Incident deduplication engine
│   │   ├── classifier.py           # Taxonomy classifier (Stages 1-7, Categories A-L)
│   │   ├── clusterer.py            # Semantic problem clustering engine
│   │   ├── metric_decomposer.py    # Funnel business metric mapper
│   │   └── hypothesis_generator.py # 8-12 Falsifiable hypothesis synthesizer
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── report_builder.py       # 14-Section Markdown report assembler
│   │   └── journey_mapper.py       # User journey reconstruction engine
│   └── qa/
│       ├── __init__.py
│       └── quality_checker.py      # Research Quality Rules validation suite
├── tests/
│   ├── test_models.py
│   ├── test_extractors.py
│   ├── test_deduplicator.py
│   ├── test_classifier.py
│   ├── test_clusterer.py
│   ├── test_report_builder.py
│   └── test_qa_checker.py
├── output/                         # Target output directory for reports & data
│   ├── research-findings.md        # Final generated report
│   ├── evidence_database.json      # Structured 19-field evidence database
│   └── qa_report.json              # QA validation results
├── problemStatement.md
├── research-brief.md
├── prd.md
└── main.py                         # Main CLI entry point
```

---

## User Review Required

> [!IMPORTANT]
> **Key Decisions & Open Questions for User Approval**
> 1. **Public Collector Ingestion Mode:** Public web platforms (Play Store, App Store, Reddit, Google Help) restrict automated web scraping without API keys. We propose supporting **two execution modes**:
>    * **API / Web Collector Mode:** Live fetching via official APIs / public endpoints.
>    * **Pre-Ingested Mock Data / File Ingestion Mode:** Loading raw text dumps from local JSON files (`data/raw_inputs/`) for deterministic, offline testing.
> 2. **LLM Provider:** We plan to use Google Gemini 1.5 Flash / Pro (via `google-genai` SDK) for structured extraction, taxonomy classification, and hypothesis generation.
> 3. **Quantitative Scoring Thresholds:** For Frequency and Severity scoring in Phase 7:
>    * `High Frequency`: ≥10 independent evidence instances.
>    * `Medium Frequency`: 4–9 instances.
>    * `Low Frequency`: 1–3 instances.

---

## Sequential Implementation Phases

---

### Phase 1: Project Scaffolding & Configuration Engine

* **Goal:** Set up the project environment, directory layout, configuration loader, CLI entry point, and execution modes (`dry-run`, `sample`, `full`).
* **Scope:**
  * Define configuration schema (`config.py` with Pydantic `BaseSettings`).
  * Create CLI argument parser (`main.py`) handling `--config`, `--mode`, `--output-dir`, and `--verbose`.
  * Implement directory creation utilities for output artifacts.
* **Inputs:** CLI arguments and default configuration file (`config/default_config.yaml`).
* **Outputs / Deliverables:** `src/config.py`, `config/default_config.yaml`, `main.py` CLI scaffolding.
* **Dependencies:** None.
* **Acceptance Check:**
  ```bash
  python main.py --mode dry-run --config config/default_config.yaml
  ```
  *Pass Criteria:* Command executes cleanly, outputs active configuration details, validates output directories, and exits with code `0`.

---

### Phase 2: Evidence Record Data Model & Storage Engine

* **Goal:** Implement the complete 19-field Evidence Record schema as a strongly typed Pydantic data model with validation rules and persistence backends.
* **Scope:**
  * Define Pydantic models in `src/models/evidence.py` covering all 19 fields explicitly: `source_platform`, `source_url`, `source_date`, `user_quote`, `user_intent`, `remembered_clues`, `forgotten_clues`, `query_attempted`, `search_strategy`, `outcome_description`, `perceived_failure_reason`, `photo_eventually_found`, `workaround_used`, `emotional_behavioral_consequence`, `failure_stage`, `failure_category`, `underlying_user_need`, `evidence_strength`, `notes`.
  * Enforce strict enum validations (`failure_stage` 1–7, `failure_category` A–L, `evidence_strength` High/Medium/Low).
  * Build SQLite / JSONL storage repository (`src/storage/repository.py`).
* **Inputs:** Raw dictionaries / JSON objects representing evidence records.
* **Outputs / Deliverables:** `src/models/evidence.py`, `src/storage/repository.py`, unit test `tests/test_models.py`.
* **Dependencies:** Phase 1.
* **Acceptance Check:**
  ```bash
  pytest tests/test_models.py
  ```
  *Pass Criteria:* All 19 fields serialize/deserialize correctly; invalid stage numbers or missing required fields raise validation errors.

---

### Phase 3: Source Platform Evidence Collection Engine

* **Goal:** Build modular collectors to fetch public user posts, reviews, and comments from target platforms.
* **Scope:**
  * Abstract base class `BaseCollector` (`src/collectors/base.py`).
  * Implement platform collectors (`play_store_collector.py`, `reddit_collector.py`, `google_help_collector.py`, `forum_collector.py`).
  * Integrate search query strategy from `research-brief.md` §5 (e.g., "can't find old photos", "remember photo sitting outside").
  * Support file-based mock payload reader for offline testing.
* **Inputs:** Search query keywords from config, target platform targets, or local raw input files.
* **Outputs / Deliverables:** `src/collectors/` modules, raw payload data structure.
* **Dependencies:** Phase 1 & Phase 2.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_collectors.py
  ```
  *Pass Criteria:* Collectors fetch/parse raw text items from test feeds or local raw files and output formatted raw evidence items containing source URLs and text quotes.

---

### Phase 4: LLM-Assisted Evidence Extraction & Schema Mapping

* **Goal:** Convert raw unstructured user posts into valid 19-field `EvidenceRecord` instances using structured LLM extraction without data fabrication.
* **Scope:**
  * Build LLM extraction pipeline in `src/processors/extractor.py`.
  * Implement prompt templates enforcing Zero Fabrication rules (verbatim quotes, exact source URLs, marking unstated items as `[Not Stated]`).
  * Enforce Pydantic JSON output parsing.
* **Inputs:** Raw text payloads from Phase 3.
* **Outputs / Deliverables:** `src/processors/extractor.py`, extracted `EvidenceRecord` collection.
* **Dependencies:** Phase 2 (Data Model) & Phase 3 (Collectors).
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_extractors.py
  ```
  *Pass Criteria:* Pass 5 sample unstructured public forum threads; extractor returns 5 fully populated 19-field `EvidenceRecord` objects where `user_quote` matches raw source text exactly.

---

### Phase 5: Incident Deduplication Engine

* **Goal:** Identify and merge duplicate posts, crossposts, or repeated discussions of the same underlying incident across platforms.
* **Scope:**
  * Implement deduplication logic in `src/processors/deduplicator.py`.
  * Match canonical URLs and compute pairwise text/quote similarity (using `rapidfuzz` string matching / embedding distance).
  * Merge duplicate records into a primary record while appending secondary source URLs to `notes` and incrementing evidence weight.
* **Inputs:** List of extracted `EvidenceRecord` objects from Phase 4.
* **Outputs / Deliverables:** `src/processors/deduplicator.py`, deduplicated record list.
* **Dependencies:** Phase 4.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_deduplicator.py
  ```
  *Pass Criteria:* Ingesting 3 records describing the same Reddit thread results in 1 merged `EvidenceRecord` with combined citation references.

---

### Phase 6: Taxonomy Classification Engine

* **Goal:** Classify every deduplicated evidence record against the 7-stage Funnel Failure Taxonomy (Stages 1–7), 12 Core Problem Categories (A–L), Memory Clues (1–9), Claim Tags (`[Observed]`, `[Inferred]`, `[Hypothesis]`), and Confidence Labels (`High`, `Medium`, `Low`).
* **Scope:**
  * Build classifier in `src/processors/classifier.py`.
  * Map evidence to Failure Stages (1: Expression, 2: Understanding, 3: Ranking, 4: Evaluation, 5: Refinement, 6: Abandonment, 7: Other).
  * Map evidence to Categories A–L (Memory, Expression, System Understanding, Ranking, Evaluation, Refinement, Temporal, Location, Context, Relationship, Visual, Text).
  * Assign mandatory `claim_tag` and `confidence_label`.
* **Inputs:** Deduplicated `EvidenceRecord` objects from Phase 5.
* **Outputs / Deliverables:** `src/processors/classifier.py`, fully classified records.
* **Dependencies:** Phase 5.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_classifier.py
  ```
  *Pass Criteria:* Benchmark test suite of 10 gold-standard records verifies 100% assignment of required taxonomy fields, claim tags, and confidence labels.

---

### Phase 7: Problem Clustering Engine

* **Goal:** Group classified evidence into named, distinct retrieval problems (e.g., "Fragmentary Event Context without Temporal Anchor") with frequency, severity, and evidence strength metrics.
* **Scope:**
  * Build clustering engine in `src/processors/clusterer.py`.
  * Group evidence using semantic feature vectors and LLM problem-cluster naming.
  * Calculate Frequency (`High/Medium/Low`), Severity (`High/Medium/Low`), and Evidence Strength without declaring a single forced winner.
  * Generate Opportunity Comparison Matrix data structure.
* **Inputs:** Classified `EvidenceRecord` objects from Phase 6.
* **Outputs / Deliverables:** `src/processors/clusterer.py`, `src/models/problem_cluster.py`, list of `ProblemCluster` objects.
* **Dependencies:** Phase 6.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_clusterer.py
  ```
  *Pass Criteria:* Clusterer processes 20+ test records and generates 3–6 distinct named problem clusters with populated frequency, severity, and confidence metrics.

---

### Phase 8: Business Metric Funnel Decomposition Engine

* **Goal:** Map classified failure stages onto the standard retrieval funnel and correlate failure loci with proxy business metrics (search-to-tap rate, query reformulation count, abandonment rate).
* **Scope:**
  * Build funnel decomposer in `src/processors/metric_decomposer.py`.
  * Calculate failure concentration across the 6 retrieval funnel stages (`User Memory` → `Ability to Express` → `System Understanding` → `Candidate Retrieval` → `Result Evaluation` → `Search Refinement` → `Outcome`).
  * Assign qualitative proxy metric impact (`[Inferred]` / `[Observed]`).
* **Inputs:** Problem clusters and classified evidence records from Phase 6 & Phase 7.
* **Outputs / Deliverables:** `src/processors/metric_decomposer.py`, Funnel Decomposition data structure.
* **Dependencies:** Phase 7.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_metric_decomposer.py
  ```
  *Pass Criteria:* Output funnel map accounts for 100% of classified records across Stages 1–7 and maps diagnostic proxy metrics for each stage.

---

### Phase 9: Falsifiable Hypothesis Generation Engine

* **Goal:** Synthesize 8–12 structured, evidence-backed interview hypotheses, each containing explicit falsification conditions, target interview questions, and observational behavioral tasks.
* **Scope:**
  * Build hypothesis synthesizer in `src/processors/hypothesis_generator.py`.
  * Enforce the 5 mandatory fields for every hypothesis: `statement`, `supporting_evidence_ids`, `falsification_condition`, `interview_question`, `behavioral_task`.
* **Inputs:** Top problem clusters and metric bottlenecks from Phase 7 & Phase 8.
* **Outputs / Deliverables:** `src/processors/hypothesis_generator.py`, `src/models/hypothesis.py`, list of `Hypothesis` objects (count: 8–12).
* **Dependencies:** Phase 7 & Phase 8.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_hypothesis_generator.py
  ```
  *Pass Criteria:* Test run produces between 8 and 12 valid hypothesis objects; every object contains a non-empty falsification condition and mapped supporting evidence IDs.

---

### Phase 10: 14-Section Report Generator & Journey Mapper

* **Goal:** Assemble all processed research findings into a single, beautifully formatted markdown document adhering strictly to the **14-Section `research-findings.md` Output Specification** from `prd.md` §5 & `research-brief.md` §20.
* **Scope:**
  * Implement journey mapper in `src/generators/journey_mapper.py` (reconstructing 5–10 representative user journeys).
  * Build report assembler in `src/generators/report_builder.py`.
  * Render all 14 required sections explicitly, including Section 4 Evidence Table (with all 19 fields), Section 8 Opportunity Matrix, Section 12 Hypotheses, Section 14 PM Takeaways, and closing `"WHAT I SHOULD DO NEXT"` action plan.
* **Inputs:** Artifacts from Phases 2 through 9.
* **Outputs / Deliverables:** `src/generators/report_builder.py`, `src/generators/journey_mapper.py`, rendered `research-findings.md`.
* **Dependencies:** Phases 2–9.
* **Acceptance Check:**
  ```bash
  python -m pytest tests/test_report_builder.py
  ```
  *Pass Criteria:* Generated markdown file contains all 14 section headers in exact order, 5–10 journey diagrams/flows in Section 6, the complete 19-field table in Section 4, and the closing action plan.

---

### Phase 11: End-to-End Pipeline Orchestration & CLI Runner

* **Goal:** Build the master CLI script (`main.py`) to execute Phases 1–10 seamlessly with progress reporting, logging, and state checkpointing.
* **Scope:**
  * Implement pipeline controller in `main.py`.
  * Add checkpointing/resume functionality to save progress between phases.
  * Support `--mode sample`, `--mode full`, `--mode dry-run`.
* **Inputs:** Configuration file, CLI parameters.
* **Outputs / Deliverables:** Complete executable `main.py` entry point.
* **Dependencies:** Phases 1–10.
* **Acceptance Check:**
  ```bash
  python main.py --mode sample --output-dir output/
  ```
  *Pass Criteria:* Pipeline completes end-to-end execution without unhandled exceptions, producing `output/research-findings.md` and `output/evidence_database.json`.

---

### Phase 12: Research Quality Rules & Validation QA Suite

* **Goal:** Implement an automated QA validator that verifies the generated report and evidence database against all 15 Research Quality Rules defined in `prd.md` §6 and `research-brief.md` §18.
* **Scope:**
  * Build QA validator module in `src/qa/quality_checker.py`.
  * Automated checks:
    1. *Zero Fabrication Check:* Verify quotes in evidence records exist in raw input text.
    2. *Citation Check:* Ensure every `source_url` is validly formatted and non-empty.
    3. *Claim Tag Check:* Ensure 100% of claims carry `[Observed]`, `[Inferred]`, or `[Hypothesis]` labels.
    4. *Confidence Tag Check:* Ensure all findings have `High/Medium/Low` confidence labels.
    5. *19-Field Completeness:* Verify zero missing fields in Section 4 evidence table.
* **Inputs:** Generated `output/research-findings.md` and `output/evidence_database.json`.
* **Outputs / Deliverables:** `src/qa/quality_checker.py`, `output/qa_report.json`.
* **Dependencies:** Phase 10 & Phase 11.
* **Acceptance Check:**
  ```bash
  python main.py --mode qa-check --output-dir output/
  ```
  *Pass Criteria:* QA validator runs over generated artifacts and produces a `qa_report.json` showing `status: PASS` with 0 fabrication warnings and 100% claim/confidence tag compliance.

---

## Verification Plan

### Automated Verification Tests
1. **Unit & Component Tests (`pytest`):**
   * Data Model & Validation: `pytest tests/test_models.py`
   * Schema Extractor: `pytest tests/test_extractors.py`
   * Deduplicator: `pytest tests/test_deduplicator.py`
   * Taxonomy Classifier: `pytest tests/test_classifier.py`
   * Problem Clusterer: `pytest tests/test_clusterer.py`
   * Metric Decomposer: `pytest tests/test_metric_decomposer.py`
   * Hypothesis Generator: `pytest tests/test_hypothesis_generator.py`
   * Report Builder: `pytest tests/test_report_builder.py`
   * QA Quality Checker: `pytest tests/test_qa_checker.py`

2. **End-to-End Test Suite:**
   * Pipeline Sample Run: `python main.py --mode sample --output-dir output/`
   * Quality Assurance Pass: `python main.py --mode qa-check --output-dir output/`

### Manual Verification Steps
1. Open `output/research-findings.md` in markdown viewer.
2. Verify that all 14 section headers are rendered in exact numerical sequence.
3. Verify Section 4 contains the complete 19-field table without missing columns or empty required fields.
4. Verify Section 6 contains 5–10 mapped user retrieval journeys.
5. Verify Section 12 contains 8–12 falsifiable hypotheses with non-empty falsification conditions.
6. Verify the closing section is titled **"WHAT I SHOULD DO NEXT"** and scopes the 5–6 person interview study.
