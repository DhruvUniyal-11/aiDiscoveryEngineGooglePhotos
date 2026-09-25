"""
File Mock Collector that loads pre-ingested raw evidence dumps.
Enables deterministic, offline testing and sample execution.
"""

import json
from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem


class FileMockCollector(BaseCollector):
    def __init__(
        self,
        platform_name: str = "Mock File Ingestion",
        filepath: Optional[Path] = None,
        enabled: bool = True,
        max_items: int = 50,
    ):
        super().__init__(platform_name, enabled, max_items)
        self.filepath = filepath or Path("data/raw_inputs/sample_evidence.json")

    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        if not self.enabled:
            return []

        if not self.filepath.exists():
            raise FileNotFoundError(f"Mock evidence file not found: {self.filepath.resolve()}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        items: List[RawEvidenceItem] = []
        for entry in raw_data:
            # Filter by platform if platform_name is specific (and not general mock)
            if self.platform_name != "Mock File Ingestion":
                if entry.get("source_platform", "").lower() != self.platform_name.lower():
                    continue

            item = RawEvidenceItem.model_validate(entry)
            items.append(item)
            if len(items) >= self.max_items:
                break

        return items
