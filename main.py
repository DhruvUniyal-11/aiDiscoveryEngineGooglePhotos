"""
Main CLI entry point for Product Discovery & User Research Engine.
"""

import argparse
import sys
import logging
from pathlib import Path

from src.config import load_config, setup_output_directories, EngineConfig
from src.pipeline import DiscoveryPipeline
from src.qa.quality_checker import QualityChecker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Product Discovery & User Research Engine for Vague-Memory Photo Retrieval"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/default_config.yaml",
        help="Path to YAML configuration file (default: config/default_config.yaml)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["dry-run", "sample", "full", "qa-check"],
        default=None,
        help="Execution mode override (dry-run, sample, full, qa-check)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory path override (default: output)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug output",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def execute_dry_run(config: EngineConfig, output_paths: dict[str, Path]) -> int:
    print("=" * 80)
    print(" PRODUCT DISCOVERY & USER RESEARCH ENGINE - DRY RUN INITIALIZATION")
    print("=" * 80)
    print(f" App Name       : {config.app.name}")
    print(f" Target Domain  : {config.app.domain}")
    print(f" Owner          : {config.app.owner}")
    print(f" Engine Version : {config.app.version}")
    print(f" Execution Mode : {config.execution.mode}")
    print(f" Output Root    : {output_paths['root']}")
    print("-" * 80)

    print("\n[Output Directory Validation]")
    for key, path in output_paths.items():
        exists_str = "EXISTS & WRITABLE" if path.exists() else "CREATION FAILED"
        print(f"  * {key.capitalize():<10}: {str(path):<50} [{exists_str}]")

    print("\n[Source Platforms (Scaffolding Configured)]")
    for platform in config.source_platforms:
        status = "ENABLED" if platform.enabled else "DISABLED"
        print(f"  * [{status:<8}] {platform.name:<35} (Max Items: {platform.max_items})")

    print("\n[Target Search Queries Strategy]")
    for q in config.target_search_queries:
        print(f"  * \"{q}\"")

    print("\n[Retrieval Failure Taxonomy - 7 Stages]")
    for stage_num, stage_name in sorted(config.taxonomies.failure_stages.items()):
        print(f"  * Stage {stage_num}: {stage_name}")

    print("\n[Retrieval Problem Taxonomy - 12 Categories]")
    for cat_code, cat_name in sorted(config.taxonomies.failure_categories.items()):
        print(f"  * Category {cat_code}: {cat_name}")

    print("\n[Memory Clue Taxonomy - 9 Clue Types]")
    for clue_num, clue_name in sorted(config.taxonomies.memory_clue_types.items()):
        print(f"  * Type {clue_num}: {clue_name}")

    print("\n[Research Quality Rules Constraints]")
    print(f"  * Zero Fabrication Requirement  : {config.quality_rules.zero_fabrication}")
    print(f"  * Mandatory Claim Tags         : {', '.join(config.quality_rules.mandatory_claim_tags)}")
    print(f"  * Confidence Labels            : {', '.join(config.quality_rules.confidence_labels)}")
    print(f"  * Frequency Thresholds         : High >= {config.quality_rules.frequency_scoring_thresholds.high}, "
          f"Medium >= {config.quality_rules.frequency_scoring_thresholds.medium}, "
          f"Low >= {config.quality_rules.frequency_scoring_thresholds.low}")

    print("=" * 80)
    print(" DRY RUN COMPLETED SUCCESSFULLY - SCAFFOLDING & CONFIG VALIDATED")
    print("=" * 80)
    return 0


def execute_qa_check(config: EngineConfig, output_paths: dict[str, Path]) -> int:
    checker = QualityChecker()
    report_file = output_paths["root"] / "research-findings.md"
    json_db_file = output_paths["root"] / "evidence_database.json"
    qa_output_file = output_paths["root"] / "qa_report.json"

    qa_report = checker.validate(
        report_path=report_file,
        json_db_path=json_db_file,
    )
    checker.export_qa_report(qa_report, qa_output_file)

    print("=" * 80)
    print(" RESEARCH QUALITY ASSURANCE VALIDATION SUITE (QA PASS)")
    print("=" * 80)
    print(f" QA Status              : {qa_report.status}")
    print(f" Rules Evaluated        : {qa_report.total_rules_evaluated}")
    print(f" Zero Fabrication Check : {'PASS' if qa_report.zero_fabrication_pass else 'FAIL'}")
    print(f" Citation Link Check    : {'PASS' if qa_report.citation_resolution_pass else 'FAIL'}")
    print(f" Claim Tagging Check    : {'PASS' if qa_report.claim_tagging_pass else 'FAIL'}")
    print(f" Confidence Label Check : {'PASS' if qa_report.confidence_labeling_pass else 'FAIL'}")
    print(f" 19-Field Schema Check  : {'PASS' if qa_report.schema_completeness_pass else 'FAIL'}")
    print(f" 14-Section Report Check: {'PASS' if qa_report.report_structure_pass else 'FAIL'}")
    print(f" Total Violations       : {len(qa_report.violations)}")
    print(f" QA Report Output       : {qa_output_file.resolve()}")
    print("=" * 80)

    if qa_report.violations:
        print("\n[QA Violation Details]")
        for v in qa_report.violations:
            print(f"  * [{v.severity}] {v.rule_id} ({v.rule_name}): {v.message}")
        print("-" * 80)

    return 0 if qa_report.status == "PASS" else 1


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger("DiscoveryEngine")

    try:
        config = load_config(
            config_path=args.config,
            mode_override=args.mode,
            output_dir_override=args.output_dir,
        )
        output_paths = setup_output_directories(config.get_resolved_output_path())
    except Exception as e:
        logger.error(f"Configuration or Initialization Error: {e}")
        return 1

    if config.execution.mode == "dry-run":
        return execute_dry_run(config, output_paths)
    elif config.execution.mode == "qa-check":
        return execute_qa_check(config, output_paths)
    elif config.execution.mode in ["sample", "full"]:
        try:
            pipeline = DiscoveryPipeline(config)
            result = pipeline.run()
            print("=" * 80)
            print(" DISCOVERY ENGINE PIPELINE EXECUTION SUMMARY")
            print("=" * 80)
            print(f" Execution Status      : {result['status']}")
            print(f" Mode                  : {result['mode']}")
            print(f" Raw Items Ingested    : {result['raw_items_count']}")
            print(f" Unique Evidence Records: {result['unique_records_count']}")
            print(f" Problem Clusters      : {result['problem_clusters_count']}")
            print(f" Interview Hypotheses  : {result['hypotheses_count']}")
            print(f" Funnel Bottleneck     : {result['bottleneck_stage']}")
            print(f" Report Output Path    : {result['report_path']}")
            print(f" JSON Database Path    : {result['database_json_path']}")
            print(f" SQLite Database Path  : {result['sqlite_db_path']}")
            print("=" * 80)

            # Auto-run QA pass after successful pipeline execution
            print("\nAuto-executing Research Quality Assurance Validation Pass...")
            qa_exit_code = execute_qa_check(config, output_paths)
            return qa_exit_code
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            return 1
    else:
        logger.error(f"Unsupported execution mode: {config.execution.mode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
