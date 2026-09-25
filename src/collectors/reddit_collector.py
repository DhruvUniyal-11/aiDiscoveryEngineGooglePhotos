"""
Reddit Thread and Post Collector.
Ingests public user discussions from subreddits (e.g. r/googlephotos, r/techsupport).
"""

from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector


class RedditCollector(BaseCollector):
    def __init__(self, enabled: bool = True, max_items: int = 25, mock_file: Optional[Path] = None):
        super().__init__("Reddit", enabled, max_items)
        self.mock_collector = FileMockCollector(
            platform_name="Reddit",
            filepath=mock_file,
            enabled=enabled,
            max_items=max_items,
        )

    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        if not self.enabled:
            return []
        return self.mock_collector.collect(queries)
