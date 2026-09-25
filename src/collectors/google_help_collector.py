"""
Google Photos Help Community Collector.
Ingests public support forum threads and troubleshooting posts.
"""

from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector


class GoogleHelpCollector(BaseCollector):
    def __init__(self, enabled: bool = True, max_items: int = 20, mock_file: Optional[Path] = None):
        super().__init__("Google Photos Help Community", enabled, max_items)
        self.mock_collector = FileMockCollector(
            platform_name="Google Photos Help Community",
            filepath=mock_file,
            enabled=enabled,
            max_items=max_items,
        )

    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        if not self.enabled:
            return []
        return self.mock_collector.collect(queries)
