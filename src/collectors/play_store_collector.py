"""
Google Play Store Review Collector.
Ingests public user reviews detailing photo retrieval failures and workarounds.
"""

from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector


class PlayStoreCollector(BaseCollector):
    def __init__(self, enabled: bool = True, max_items: int = 20, mock_file: Optional[Path] = None):
        super().__init__("Google Play Store", enabled, max_items)
        self.mock_collector = FileMockCollector(
            platform_name="Google Play Store",
            filepath=mock_file,
            enabled=enabled,
            max_items=max_items,
        )

    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        if not self.enabled:
            return []
        # In offline/mock mode, delegate to mock file ingestion
        return self.mock_collector.collect(queries)
