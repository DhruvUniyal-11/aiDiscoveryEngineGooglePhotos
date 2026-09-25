"""
Generic Forum & Social Media Collector.
Ingests public comments and posts from Apple App Store, YouTube, X/Twitter, and tech forums.
"""

from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector


class ForumCollector(BaseCollector):
    def __init__(self, platform_name: str, enabled: bool = True, max_items: int = 15, mock_file: Optional[Path] = None):
        super().__init__(platform_name, enabled, max_items)
        self.mock_collector = FileMockCollector(
            platform_name=platform_name,
            filepath=mock_file,
            enabled=enabled,
            max_items=max_items,
        )

    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        if not self.enabled:
            return []
        return self.mock_collector.collect(queries)
