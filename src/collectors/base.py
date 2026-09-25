"""
Base Collector interface and RawEvidenceItem data model.
Adheres strictly to prd.md Section 2 (FR-1) and research-brief.md Section 4 & 5.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


class RawEvidenceItem(BaseModel):
    raw_id: str = Field(..., description="Unique raw evidence item ID")
    source_platform: str = Field(..., description="Platform name (Play Store, Reddit, etc.)")
    source_url: str = Field(..., description="Canonical source URL")
    source_date: str = Field(default="[Not Stated]", description="Publication date if available")
    raw_text: str = Field(..., description="Verbatim raw user text / review / post")
    author_or_user: str = Field(default="Anonymous", description="Author or username if present")
    search_query: Optional[str] = Field(default=None, description="Search query string that matched item")


class BaseCollector(ABC):
    def __init__(self, platform_name: str, enabled: bool = True, max_items: int = 20):
        self.platform_name = platform_name
        self.enabled = enabled
        self.max_items = max_items

    @abstractmethod
    def collect(self, queries: List[str]) -> List[RawEvidenceItem]:
        """
        Collects raw user evidence items given search queries.
        """
        pass
