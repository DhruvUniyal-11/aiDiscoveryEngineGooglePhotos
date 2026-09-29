"""
Google Play Store Review Collector with Live Scraping and Mock Fallback.
Ingests public user reviews detailing photo retrieval failures and workarounds.
"""

import logging
from pathlib import Path
from typing import List, Optional
from src.collectors.base import BaseCollector, RawEvidenceItem
from src.collectors.file_mock_collector import FileMockCollector

logger = logging.getLogger(__name__)

# Keywords indicating search/retrieval context
RELEVANT_KEYWORDS = [
    "search", "find", "locate", "receipt", "screenshot", "date", "filter",
    "album", "lost", "ticket", "face", "photo", "picture", "scan", "ocr"
]


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

        items: List[RawEvidenceItem] = []
        try:
            from google_play_scraper import reviews, Sort
            logger.info(f"Fetching up to 200 live Google Play Store reviews for com.google.android.apps.photos...")
            result, _ = reviews(
                'com.google.android.apps.photos',
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=200,
            )

            for idx, r in enumerate(result):
                content = r.get("content", "")
                content_lower = content.lower()

                # Filter for relevant search/retrieval complaints
                if any(kw in content_lower for kw in RELEVANT_KEYWORDS) and len(content.split()) >= 8:
                    review_id = r.get("reviewId") or f"gp-live-{idx}"
                    date_str = r.get("at").strftime("%Y-%m-%d") if r.get("at") else "[Not Stated]"
                    user_name = r.get("userName") or "Play Store User"

                    item = RawEvidenceItem(
                        raw_id=f"RAW-PLAYSTORE-LIVE-{idx+1:03d}",
                        source_platform="Google Play Store",
                        source_url=f"https://play.google.com/store/apps/details?id=com.google.android.apps.photos&reviewId={review_id}",
                        source_date=date_str,
                        raw_text=content,
                        author_or_user=user_name,
                        search_query="live play store review search",
                    )
                    items.append(item)
                    if len(items) >= self.max_items:
                        break

            logger.info(f"Harvested {len(items)} live Google Play Store evidence items.")
        except Exception as e:
            logger.warning(f"Live Google Play Store scraping failed or unavailable ({e}). Falling back to mock dataset.")
            items = []

        if not items:
            items = self.mock_collector.collect(queries)

        return items
