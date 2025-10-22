"""Async search functionality using Perplexity API."""

import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List
import logging
from datetime import datetime

from .config import config
from .models import SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Exception raised for search failures."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def search_single(query: str, session: aiohttp.ClientSession, category: str = "general") -> SearchResult:
    """Execute a single search query via Perplexity API.

    Args:
        query: Search query string
        session: aiohttp ClientSession
        category: Category of the query

    Returns:
        SearchResult object

    Raises:
        SearchError: If search fails after retries
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.perplexity_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "return_related_questions": False,
        "search_domain_filter": [],
        "temperature": 0.2,
        "top_p": 0.9,
        "return_images": False
    }

    try:
        async with session.post(
            url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=config.search_timeout)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Perplexity API error {response.status}: {error_text}")
                raise SearchError(f"API returned status {response.status}: {error_text}")

            data = await response.json()

            # Extract response text
            response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Extract sources from citations
            sources = []
            if "citations" in data:
                sources = data["citations"]
            elif "search_results" in data:
                # Newer API format
                sources = [result.get("url", "") for result in data.get("search_results", [])]

            return SearchResult(
                query=query,
                response_text=response_text,
                sources=sources,
                timestamp=datetime.now(),
                category=category,
                success=True,
                error_message=None
            )

    except asyncio.TimeoutError as e:
        logger.error(f"Search timed out for query: {query}")
        # Re-raise to trigger retry mechanism
        raise SearchError(f"Search timed out after {config.search_timeout}s")
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        raise SearchError(f"Search failed: {e}")


async def search_batch(
    queries: List[SearchQuery],
    max_concurrent: int = None
) -> List[SearchResult]:
    """Execute multiple queries with concurrency control.

    Args:
        queries: List of SearchQuery objects
        max_concurrent: Max concurrent requests (defaults to config)

    Returns:
        List of SearchResult objects
    """
    if max_concurrent is None:
        max_concurrent = config.max_concurrent_searches

    logger.info(f"Starting batch search with {len(queries)} queries, max concurrent: {max_concurrent}")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_search(query: SearchQuery, session: aiohttp.ClientSession):
        async with semaphore:
            try:
                result = await search_single(query.query_text, session, query.category)
                if result.success:
                    logger.debug(f"✓ Search succeeded: {query.query_text[:50]}...")
                return result
            except Exception as e:
                logger.error(f"Search failed for '{query.query_text}': {e}")
                return SearchResult(
                    query=query.query_text,
                    response_text="",
                    sources=[],
                    timestamp=datetime.now(),
                    category=query.category,
                    success=False,
                    error_message=str(e)
                )

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_search(q, session) for q in queries]
        results = await asyncio.gather(*tasks)

    successful = sum(1 for r in results if r.success)
    logger.info(f"Batch search complete: {successful}/{len(queries)} successful")

    return results
