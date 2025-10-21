"""Data models for Ultra Deep Research."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class ReconnaissanceContext:
    """Context gathered during reconnaissance phase."""

    original_topic: str
    overview_query: str
    overview_result: str
    key_subtopics: List[str]
    key_entities: List[str]
    terminology: List[str]
    research_angles: List[str]
    timestamp: datetime


@dataclass
class SearchQuery:
    """Individual search query with metadata."""

    query_text: str
    category: str
    priority: int = 1


@dataclass
class SearchResult:
    """Result from a single search query."""

    query: str
    response_text: str
    sources: List[str]
    timestamp: datetime
    category: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class AggregatedResearch:
    """Aggregated research results from all queries."""

    topic: str
    reconnaissance: ReconnaissanceContext
    results_by_category: Dict[str, List[SearchResult]]
    all_sources: List[str]
    total_queries: int
    successful_queries: int
    failed_queries: int
    timestamp: datetime
