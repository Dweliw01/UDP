"""Basic tests for Ultra Deep Research."""

import pytest
from datetime import datetime
from src.models import SearchQuery, ReconnaissanceContext, SearchResult, AggregatedResearch


def test_search_query_creation():
    """Test SearchQuery dataclass creation."""
    query = SearchQuery(
        query_text="test query",
        category="foundational"
    )
    assert query.query_text == "test query"
    assert query.category == "foundational"
    assert query.priority == 1


def test_search_query_with_priority():
    """Test SearchQuery with custom priority."""
    query = SearchQuery(
        query_text="important query",
        category="technical",
        priority=5
    )
    assert query.priority == 5


def test_reconnaissance_context_creation():
    """Test ReconnaissanceContext dataclass creation."""
    context = ReconnaissanceContext(
        original_topic="test topic",
        overview_query="test query",
        overview_result="test result",
        key_subtopics=["sub1", "sub2"],
        key_entities=["entity1"],
        terminology=["term1"],
        research_angles=["angle1"],
        timestamp=datetime.now()
    )
    assert context.original_topic == "test topic"
    assert len(context.key_subtopics) == 2
    assert len(context.key_entities) == 1


def test_search_result_success():
    """Test successful SearchResult."""
    result = SearchResult(
        query="test query",
        response_text="test response",
        sources=["https://example.com"],
        timestamp=datetime.now(),
        category="foundational",
        success=True
    )
    assert result.success is True
    assert result.error_message is None
    assert len(result.sources) == 1


def test_search_result_failure():
    """Test failed SearchResult."""
    result = SearchResult(
        query="test query",
        response_text="",
        sources=[],
        timestamp=datetime.now(),
        category="technical",
        success=False,
        error_message="API error"
    )
    assert result.success is False
    assert result.error_message == "API error"


def test_aggregated_research_creation():
    """Test AggregatedResearch dataclass creation."""
    recon = ReconnaissanceContext(
        original_topic="test",
        overview_query="query",
        overview_result="result",
        key_subtopics=["sub1"],
        key_entities=["entity1"],
        terminology=["term1"],
        research_angles=["angle1"],
        timestamp=datetime.now()
    )

    aggregated = AggregatedResearch(
        topic="test topic",
        reconnaissance=recon,
        results_by_category={"foundational": [], "technical": []},
        all_sources=["https://example.com"],
        total_queries=100,
        successful_queries=95,
        failed_queries=5,
        timestamp=datetime.now()
    )

    assert aggregated.topic == "test topic"
    assert aggregated.total_queries == 100
    assert aggregated.successful_queries == 95
    assert aggregated.failed_queries == 5
    assert len(aggregated.all_sources) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
