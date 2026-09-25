"""
End-to-End Discovery Pipeline Orchestrator.
Chains Phases 1 through 10 into an autonomous, fault-tolerant research processing workflow.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.config import EngineConfig, setup_output_directories
from src.storage.repository import EvidenceRepository
from src.collectors.collector_factory import run_all_collectors
from src.processors.extractor import EvidenceExtractor
from src.processors.deduplicator import EvidenceDeduplicator
from src.processors.classifier import TaxonomyClassifier
from src.processors.clusterer import ProblemClusterer
from src.processors.metric_decomposer import BusinessMetricDecomposer
from src.processors.hypothesis_generator import HypothesisGenerator
from src.generators.report_builder import ReportBuilder

logger = logging.getLogger("DiscoveryEngine.Pipeline")


class DiscoveryPipeline:
    """
    Master pipeline orchestrator that executes end-to-end discovery processing.
    """

    def __init__(self, config: EngineConfig):
        self.config = config
        self.output_paths = setup_output_directories(config.get_resolved_output_path())
        self.db_path = self.output_paths["data"] / "evidence.db"
        self.repository = EvidenceRepository(self.db_path)

        # Processors & Generators
        self.extractor = EvidenceExtractor()
        self.deduplicator = EvidenceDeduplicator()
        self.classifier = TaxonomyClassifier()
        self.clusterer = ProblemClusterer(
            high_freq_threshold=config.quality_rules.frequency_scoring_thresholds.high,
            med_freq_threshold=config.quality_rules.frequency_scoring_thresholds.medium,
        )
        self.metric_decomposer = BusinessMetricDecomposer()
        self.hypothesis_generator = HypothesisGenerator()
        self.report_builder = ReportBuilder()

    def run(self) -> Dict[str, Any]:
        """
        Executes all pipeline phases sequentially.
        """
        logger.info("==========================================================")
        logger.info(f" STARTING DISCOVERY ENGINE PIPELINE (Mode: {self.config.execution.mode})")
        logger.info("==========================================================")

        # Step 1: Ingest Raw Evidence Items (Phase 3)
        logger.info("[Step 1/7] Ingesting raw evidence items across configured platforms...")
        mock_file = Path("data/raw_inputs/sample_evidence.json")
        raw_items = run_all_collectors(self.config, mock_file=mock_file)
        logger.info(f" -> Ingested {len(raw_items)} raw text evidence items.")

        # Step 2: Extract 19-Field Evidence Records (Phase 4)
        logger.info("[Step 2/7] Extracting 19-field EvidenceRecord instances (Zero Fabrication enforced)...")
        extracted_records = self.extractor.extract_batch(raw_items)
        logger.info(f" -> Extracted {len(extracted_records)} structured evidence records.")

        # Step 3: Deduplicate Crossposts & Repeated Discussions (Phase 5)
        logger.info("[Step 3/7] Running incident deduplication engine...")
        deduped_records = self.deduplicator.deduplicate_records(extracted_records)
        logger.info(f" -> Deduplicated down to {len(deduped_records)} unique evidence records.")

        # Step 4: Classify against Research Taxonomies (Phase 6)
        logger.info("[Step 4/7] Classifying evidence against 7 failure stages & 12 problem categories...")
        classified_records = self.classifier.classify_batch(deduped_records)

        # Save classified records to SQLite and JSON repositories
        self.repository.clear_all()
        for rec in classified_records:
            self.repository.save_record(rec)

        jsonl_path = self.output_paths["data"] / "evidence_database.jsonl"
        json_path = self.output_paths["root"] / "evidence_database.json"
        self.repository.export_to_jsonl(jsonl_path)
        self.repository.export_to_json(json_path)
        logger.info(f" -> Saved {len(classified_records)} classified records to SQLite & exported JSON databases.")

        # Step 5: Cluster Problems & Build Opportunity Matrix (Phase 7)
        logger.info("[Step 5/7] Clustering problem patterns and constructing Opportunity Matrix...")
        clusters = self.clusterer.cluster_records(classified_records)
        matrix = self.clusterer.build_opportunity_matrix(clusters)
        logger.info(f" -> Created {len(clusters)} distinct named problem clusters.")

        # Step 6: Decompose Business Metric Funnel & Synthesize Hypotheses (Phases 8 & 9)
        logger.info("[Step 6/7] Decomposing business metric funnel & synthesizing falsifiable hypotheses...")
        funnel = self.metric_decomposer.decompose(classified_records)
        hypotheses = self.hypothesis_generator.generate_hypotheses(clusters, funnel)
        logger.info(f" -> Identified bottleneck: {funnel.bottleneck_stage_name} ({funnel.bottleneck_concentration_pct}%).")
        logger.info(f" -> Synthesized {len(hypotheses)} falsifiable user interview hypotheses.")

        # Step 7: Assemble 14-Section Markdown Report (Phase 10)
        logger.info("[Step 7/7] Assembling 14-section research-findings.md report...")
        report_path = self.output_paths["root"] / "research-findings.md"
        report_content = self.report_builder.build_report(
            records=classified_records,
            clusters=clusters,
            matrix=matrix,
            funnel=funnel,
            hypotheses=hypotheses,
            output_filepath=report_path,
        )

        logger.info("==========================================================")
        logger.info(f" PIPELINE COMPLETED SUCCESSFULLY! Report: {report_path.resolve()}")
        logger.info("==========================================================")

        return {
            "status": "SUCCESS",
            "mode": self.config.execution.mode,
            "raw_items_count": len(raw_items),
            "unique_records_count": len(classified_records),
            "problem_clusters_count": len(clusters),
            "hypotheses_count": len(hypotheses),
            "bottleneck_stage": funnel.bottleneck_stage_name,
            "report_path": str(report_path),
            "database_json_path": str(json_path),
            "database_jsonl_path": str(jsonl_path),
            "sqlite_db_path": str(self.db_path),
        }
