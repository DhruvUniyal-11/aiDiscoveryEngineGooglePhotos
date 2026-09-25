"""
Collector Factory module.
Creates and orchestrates evidence collectors based on EngineConfig settings.
"""

from pathlib import Path
from typing import List, Optional
from src.config import EngineConfig, PlatformConfig
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.play_store_collector import PlayStoreCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.google_help_collector import GoogleHelpCollector
from src.collectors.forum_collector import ForumCollector
from src.collectors.file_mock_collector import FileMockCollector


def create_collector_for_platform(
    platform: PlatformConfig,
    mock_file: Optional[Path] = None
) -> BaseCollector:
    name_lower = platform.name.lower()
    if "play store" in name_lower:
        return PlayStoreCollector(enabled=platform.enabled, max_items=platform.max_items, mock_file=mock_file)
    elif "reddit" in name_lower:
        return RedditCollector(enabled=platform.enabled, max_items=platform.max_items, mock_file=mock_file)
    elif "help community" in name_lower or "google help" in name_lower:
        return GoogleHelpCollector(enabled=platform.enabled, max_items=platform.max_items, mock_file=mock_file)
    else:
        return ForumCollector(platform_name=platform.name, enabled=platform.enabled, max_items=platform.max_items, mock_file=mock_file)


def run_all_collectors(
    config: EngineConfig,
    mock_file: Optional[Path] = None
) -> List[RawEvidenceItem]:
    """
    Executes all enabled platform collectors and returns combined raw evidence items.
    """
    all_items: List[RawEvidenceItem] = []
    queries = config.target_search_queries

    # If mock_file is present or in offline mode, fall back to FileMockCollector if platform collectors return 0
    for platform in config.source_platforms:
        if not platform.enabled:
            continue
        collector = create_collector_for_platform(platform, mock_file=mock_file)
        items = collector.collect(queries)
        all_items.extend(items)

    # Fallback to general file mock collector if zero items harvested
    if not all_items and mock_file and mock_file.exists():
        fallback_collector = FileMockCollector(filepath=mock_file, max_items=config.execution.max_evidence_items)
        all_items = fallback_collector.collect(queries)

    return all_items
