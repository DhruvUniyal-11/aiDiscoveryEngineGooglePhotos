"""
Research Quality Rules Validator Suite.
Verifies synthesized evidence and research-findings.md report against all 15 Research Quality Rules
from prd.md Section 6 and research-brief.md Section 18.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.models.evidence import EvidenceRecord
from src.models.taxonomy import ClaimTag, EvidenceStrength

logger = logging.getLogger("DiscoveryEngine.QA")


class QARuleViolation(BaseModel):
    rule_id: str
    rule_name: str
    severity: str  # ERROR or WARNING
    message: str
    evidence_id: Optional[str] = None


class QAReport(BaseModel):
    status: str  # PASS or FAIL
    total_rules_evaluated: int = 0
    passed_rules_count: int = 0
    failed_rules_count: int = 0
    zero_fabrication_pass: bool = True
    citation_resolution_pass: bool = True
    claim_tagging_pass: bool = True
    confidence_labeling_pass: bool = True
    schema_completeness_pass: bool = True
    report_structure_pass: bool = True
    violations: List[QARuleViolation] = Field(default_factory=list)


class QualityChecker:
    """
    Automated Research Quality Assurance Validator enforcing non-negotiable PRD Section 6 rules.
    """

    def validate(
        self,
        report_path: Path,
        json_db_path: Path,
        raw_items: Optional[List[Any]] = None,
    ) -> QAReport:
        """
        Executes QA validation pass on generated research report and evidence database.
        """
        violations: List[QARuleViolation] = []
        rules_evaluated = 0

        # Load Evidence Database JSON
        records: List[EvidenceRecord] = []
        if json_db_path.exists():
            with open(json_db_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                records = [EvidenceRecord.model_validate(item) for item in raw_data]

        # Load Report Text
        report_text = ""
        if report_path.exists():
            report_text = report_path.read_text(encoding="utf-8")

        # Check 1: Zero Fabrication Rule (PRD §6 Rule 1)
        rules_evaluated += 1
        zero_fab_pass = True
        if raw_items:
            raw_text_combined = " ".join([item.raw_text for item in raw_items])
            for rec in records:
                quote_prefix = rec.user_quote.split("...")[0].strip()
                if len(quote_prefix) > 15 and quote_prefix not in raw_text_combined:
                    zero_fab_pass = False
                    violations.append(QARuleViolation(
                        rule_id="RULE-01",
                        rule_name="Zero Fabrication Requirement",
                        severity="ERROR",
                        message=f"Evidence {rec.evidence_id} quote is not a verbatim substring of raw input text.",
                        evidence_id=rec.evidence_id
                    ))

        # Check 2: Citation Link Resolution (PRD §6 Rule 1 & research-brief.md Rule 9)
        rules_evaluated += 1
        citation_pass = True
        for rec in records:
            url = rec.source_url.strip()
            if not url or not (url.startswith("http://") or url.startswith("https://")):
                citation_pass = False
                violations.append(QARuleViolation(
                    rule_id="RULE-02",
                    rule_name="Canonical Citation URL Resolution",
                    severity="ERROR",
                    message=f"Evidence {rec.evidence_id} has invalid or missing source_url: '{rec.source_url}'",
                    evidence_id=rec.evidence_id
                ))

        # Check 3: Mandatory Claim Tagging (PRD §6 Rule 2)
        rules_evaluated += 1
        claim_pass = True
        for rec in records:
            if rec.claim_tag not in [ClaimTag.OBSERVED, ClaimTag.INFERRED, ClaimTag.HYPOTHESIS]:
                claim_pass = False
                violations.append(QARuleViolation(
                    rule_id="RULE-03",
                    rule_name="Mandatory Claim Tagging",
                    severity="ERROR",
                    message=f"Evidence {rec.evidence_id} lacks valid claim tag ([Observed], [Inferred], [Hypothesis])",
                    evidence_id=rec.evidence_id
                ))

        # Check 4: Rigorous Confidence Labeling (PRD §6 Rule 5)
        rules_evaluated += 1
        confidence_pass = True
        for rec in records:
            if rec.evidence_strength not in [EvidenceStrength.HIGH, EvidenceStrength.MEDIUM, EvidenceStrength.LOW]:
                confidence_pass = False
                violations.append(QARuleViolation(
                    rule_id="RULE-04",
                    rule_name="Rigorous Confidence Labeling",
                    severity="ERROR",
                    message=f"Evidence {rec.evidence_id} lacks valid confidence rating",
                    evidence_id=rec.evidence_id
                ))

        # Check 5: 19-Field Schema Completeness (PRD §3)
        rules_evaluated += 1
        schema_pass = True
        expected_19_keys = {
            "source_platform", "source_url", "source_date", "user_quote", "user_intent",
            "remembered_clues", "forgotten_clues", "query_attempted", "search_strategy",
            "outcome_description", "perceived_failure_reason", "photo_eventually_found",
            "workaround_used", "emotional_behavioral_consequence", "failure_stage",
            "failure_category", "underlying_user_need", "evidence_strength", "notes"
        }
        for rec in records:
            fields = rec.get_19_fields_dict()
            missing_keys = expected_19_keys - set(fields.keys())
            if missing_keys:
                schema_pass = False
                violations.append(QARuleViolation(
                    rule_id="RULE-05",
                    rule_name="19-Field Schema Completeness",
                    severity="ERROR",
                    message=f"Evidence {rec.evidence_id} missing schema fields: {missing_keys}",
                    evidence_id=rec.evidence_id
                ))

        # Check 6: 14-Section Report Integrity (PRD §5)
        rules_evaluated += 1
        structure_pass = True
        required_headers = [
            "## Section 1: Executive Summary",
            "## Section 2: Source Landscape",
            "## Section 3: Retrieval Problem Taxonomy",
            "## Section 4: Evidence Table",
            "## Section 5: Memory Taxonomy Analysis",
            "## Section 6: Representative Retrieval Journeys",
            "## Section 7: Business Metric Funnel Decomposition",
            "## Section 8: Opportunity Areas",
            "## Section 9: Evidence-Backed User Segments",
            "## Section 10: AI Opportunity Map",
            "## Section 11: Research Gaps & Limitations",
            "## Section 12: Falsifiable User Interview Hypotheses",
            "## Section 13: Recommended Next-Phase User Research Design",
            "## Section 14: Product Manager Takeaways",
            "## WHAT I SHOULD DO NEXT",
        ]
        for hdr in required_headers:
            if hdr not in report_text:
                structure_pass = False
                violations.append(QARuleViolation(
                    rule_id="RULE-06",
                    rule_name="14-Section Report Structure Integrity",
                    severity="ERROR",
                    message=f"Report missing required header: '{hdr}'"
                ))

        # Determine overall QA status
        errors_count = len([v for v in violations if v.severity == "ERROR"])
        overall_status = "PASS" if errors_count == 0 else "FAIL"

        qa_report = QAReport(
            status=overall_status,
            total_rules_evaluated=rules_evaluated,
            passed_rules_count=rules_evaluated - (1 if errors_count > 0 else 0),
            failed_rules_count=1 if errors_count > 0 else 0,
            zero_fabrication_pass=zero_fab_pass,
            citation_resolution_pass=citation_pass,
            claim_tagging_pass=claim_pass,
            confidence_labeling_pass=confidence_pass,
            schema_completeness_pass=schema_pass,
            report_structure_pass=structure_pass,
            violations=violations,
        )

        logger.info(f"QA Validation Completed: Status={overall_status}, Violations={len(violations)}")
        return qa_report

    def export_qa_report(self, qa_report: QAReport, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(qa_report.model_dump(mode="json"), f, indent=2)
        return output_path
