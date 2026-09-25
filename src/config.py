"""
Configuration loader and validator module for Product Discovery & User Research Engine.
"""

from pathlib import Path
from typing import Dict, List, Literal, Optional
import yaml
from pydantic import BaseModel, Field, field_validator


class AppMetadata(BaseModel):
    name: str
    domain: str
    owner: str
    version: str


class ExecutionConfig(BaseModel):
    mode: Literal["dry-run", "sample", "full", "qa-check"] = "sample"
    output_dir: str = "output"
    log_level: str = "INFO"
    max_evidence_items: int = Field(default=50, ge=1)

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("output_dir cannot be empty")
        return v.strip()


class PlatformConfig(BaseModel):
    name: str
    enabled: bool = True
    max_items: int = Field(default=20, ge=1)


class TaxonomiesConfig(BaseModel):
    failure_stages: Dict[int, str]
    failure_categories: Dict[str, str]
    memory_clue_types: Dict[int, str]

    @field_validator("failure_stages")
    @classmethod
    def validate_stages(cls, v: Dict[int, str]) -> Dict[int, str]:
        expected_stages = {1, 2, 3, 4, 5, 6, 7}
        missing = expected_stages - set(v.keys())
        if missing:
            raise ValueError(f"Missing required failure stage numbers: {missing}")
        return v

    @field_validator("failure_categories")
    @classmethod
    def validate_categories(cls, v: Dict[str, str]) -> Dict[str, str]:
        expected_categories = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"}
        missing = expected_categories - set(v.keys())
        if missing:
            raise ValueError(f"Missing required failure category keys: {missing}")
        return v


class FrequencyThresholds(BaseModel):
    high: int = 10
    medium: int = 4
    low: int = 1


class QualityRulesConfig(BaseModel):
    zero_fabrication: bool = True
    mandatory_claim_tags: List[str]
    confidence_labels: List[str]
    frequency_scoring_thresholds: FrequencyThresholds


class EngineConfig(BaseModel):
    app: AppMetadata
    execution: ExecutionConfig
    source_platforms: List[PlatformConfig]
    target_search_queries: List[str]
    taxonomies: TaxonomiesConfig
    quality_rules: QualityRulesConfig

    def get_resolved_output_path(self) -> Path:
        return Path(self.execution.output_dir).resolve()


def setup_output_directories(output_dir: Path) -> Dict[str, Path]:
    """
    Creates and validates required output directory structure.
    """
    resolved = output_dir.resolve()
    subdirs = {
        "root": resolved,
        "data": resolved / "data",
        "logs": resolved / "logs",
        "reports": resolved / "reports"
    }

    for dir_path in subdirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return subdirs


def load_config(
    config_path: str | Path,
    mode_override: Optional[str] = None,
    output_dir_override: Optional[str] = None
) -> EngineConfig:
    """
    Loads YAML configuration file and applies CLI overrides.
    """
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path.resolve()}")

    with open(path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    if not isinstance(raw_data, dict):
        raise ValueError(f"Invalid YAML structure in {path.resolve()}")

    # Apply CLI overrides if provided
    if mode_override:
        if "execution" not in raw_data or raw_data["execution"] is None:
            raw_data["execution"] = {}
        raw_data["execution"]["mode"] = mode_override

    if output_dir_override:
        if "execution" not in raw_data or raw_data["execution"] is None:
            raw_data["execution"] = {}
        raw_data["execution"]["output_dir"] = output_dir_override

    config = EngineConfig.model_validate(raw_data)
    setup_output_directories(config.get_resolved_output_path())
    return config
