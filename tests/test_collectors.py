"""
Unit tests for Source Platform Evidence Collection Engine.
Phase 3 Acceptance Check Suite per implementation-plan.md.
"""

import pytest
from pathlib import Path
from src.config import load_config
from src.collectors.base import RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector
from src.collectors.play_store_collector import PlayStoreCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.google_help_collector import GoogleHelpCollector
from src.collectors.forum_collector import ForumCollector
from src.collectors.collector_factory import run_all_collectors, create_collector_for_platform


def test_raw_evidence_item_model():
    item = RawEvidenceItem(
        raw_id="RAW-TEST-001",
        source_platform="Reddit",
        source_url="https://reddit.com/r/googlephotos/comments/test",
        source_date="2026-05-01",
        raw_text="I remember the café sitting outside",
        author_or_user="test_user",
        search_query="can't find old photos"
    )
    assert item.raw_id == "RAW-TEST-001"
    assert item.source_platform == "Reddit"
    assert item.source_url.startswith("https://")
    assert "café" in item.raw_text


def test_file_mock_collector_ingestion():
    mock_file = Path("data/raw_inputs/sample_evidence.json")
    assert mock_file.exists()

    collector = FileMockCollector(filepath=mock_file)
    items = collector.collect(queries=["can't find old photos"])

    assert len(items) > 0
    for item in items:
        assert isinstance(item, RawEvidenceItem)
        assert item.raw_id.startswith("RAW-")
        assert len(item.source_url) > 0
        assert len(item.raw_text) > 0


def test_platform_specific_collectors():
    mock_file = Path("data/raw_inputs/sample_evidence.json")

    reddit_col = RedditCollector(mock_file=mock_file)
    reddit_items = reddit_col.collect(["test query"])
    assert len(reddit_items) > 0
    assert all(i.source_platform == "Reddit" for i in reddit_items)

    play_col = PlayStoreCollector(mock_file=mock_file)
    play_items = play_col.collect(["test query"])
    assert len(play_items) > 0
    assert all(i.source_platform == "Google Play Store" for i in play_items)

    help_col = GoogleHelpCollector(mock_file=mock_file)
    help_items = help_col.collect(["test query"])
    assert len(help_items) > 0
    assert all(i.source_platform == "Google Photos Help Community" for i in help_items)


def test_collector_factory_run_all():
    config = load_config("config/default_config.yaml", mode_override="sample")
    mock_file = Path("data/raw_inputs/sample_evidence.json")

    all_items = run_all_collectors(config, mock_file=mock_file)
    assert len(all_items) >= 5

    # Verify every harvested item has a valid source URL and non-empty quote text
    for item in all_items:
        assert item.source_url.startswith("http")
        assert len(item.raw_text) > 20
        assert item.source_platform in [
            "Google Play Store", "Apple App Store", "Reddit",
            "Google Photos Help Community", "YouTube", "X/Twitter & Social Media",
            "Public Technology Forums"
        ]
