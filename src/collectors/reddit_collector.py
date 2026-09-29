"""
Reddit Thread and Post Collector with Live API scraping and Mock Fallback.
Ingests public user discussions from subreddits (e.g. r/googlephotos, r/techsupport).
"""

import logging
import requests
from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector

logger = logging.getLogger(__name__)

RELEVANT_KEYWORDS = [
    "search", "find", "locate", "receipt", "screenshot", "date", "filter",
    "album", "lost", "ticket", "face", "photo", "picture", "scan", "ocr", "memory"
]


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

        items: List[RawEvidenceItem] = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-DiscoveryEngine/1.0"}
        search_urls = [
            "https://www.reddit.com/r/googlephotos/search.json?q=search&restrict_sr=1&sort=relevance&limit=50",
            "https://www.reddit.com/r/techsupport/search.json?q=google+photos+search&restrict_sr=1&sort=relevance&limit=25",
        ]

        try:
            for url in search_urls:
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for idx, child in enumerate(children):
                        post_data = child.get("data", {})
                        title = post_data.get("title", "")
                        selftext = post_data.get("selftext", "")
                        full_text = f"{title}. {selftext}".strip()

                        if any(kw in full_text.lower() for kw in RELEVANT_KEYWORDS) and len(full_text.split()) >= 10:
                            post_id = post_data.get("id", f"reddit-{idx}")
                            permalink = post_data.get("permalink", "")
                            author = post_data.get("author", "anonymous")
                            source_url = f"https://www.reddit.com{permalink}" if permalink else f"https://www.reddit.com/r/googlephotos/comments/{post_id}"

                            item = RawEvidenceItem(
                                raw_id=f"RAW-REDDIT-LIVE-{len(items)+1:03d}",
                                source_platform="Reddit",
                                source_url=source_url,
                                source_date="[Not Stated]",
                                raw_text=full_text,
                                author_or_user=f"u/{author}",
                                search_query="r/googlephotos live search",
                            )
                            items.append(item)
                            if len(items) >= self.max_items:
                                break
                if len(items) >= self.max_items:
                    break

            logger.info(f"Harvested {len(items)} live Reddit evidence items.")
        except Exception as e:
            logger.warning(f"Live Reddit API fetching failed ({e}). Falling back to mock dataset.")
            items = []

        if not items:
            items = self.mock_collector.collect(queries)

        return items
