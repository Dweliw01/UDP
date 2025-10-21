"""Result aggregation and structuring."""

import logging
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

from .models import SearchResult, ReconnaissanceContext, AggregatedResearch

logger = logging.getLogger(__name__)


def aggregate_results(
    topic: str,
    results: List[SearchResult],
    recon_context: ReconnaissanceContext
) -> AggregatedResearch:
    """Aggregate search results into structured format.

    Args:
        topic: Research topic
        results: List of search results
        recon_context: Context from reconnaissance

    Returns:
        AggregatedResearch object
    """
    logger.info(f"Aggregating {len(results)} search results")

    # Separate successful and failed results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    logger.info(f"Successful: {len(successful)}, Failed: {len(failed)}")

    # Group by category
    results_by_category = defaultdict(list)
    for result in successful:
        results_by_category[result.category].append(result)

    # Collect all unique sources
    all_sources = []
    seen_sources = set()
    for result in successful:
        for source in result.sources:
            if source not in seen_sources:
                all_sources.append(source)
                seen_sources.add(source)

    logger.info(f"Collected {len(all_sources)} unique sources")

    # Create aggregated research object
    aggregated = AggregatedResearch(
        topic=topic,
        reconnaissance=recon_context,
        results_by_category=dict(results_by_category),
        all_sources=all_sources,
        total_queries=len(results),
        successful_queries=len(successful),
        failed_queries=len(failed),
        timestamp=datetime.now()
    )

    # Log summary by category
    for category, cat_results in results_by_category.items():
        logger.info(f"  {category}: {len(cat_results)} results")

    return aggregated
