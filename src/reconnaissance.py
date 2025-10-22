"""Reconnaissance phase - Initial context gathering."""

import anthropic
from typing import Tuple
import logging
import json
from datetime import datetime

from .config import config
from .models import ReconnaissanceContext, SearchResult
from .searcher import search_single
import aiohttp

logger = logging.getLogger(__name__)

# Import the EXACT prompt from PROMPTS.md Section 1.1
OVERVIEW_QUERY_PROMPT = """Generate ONE comprehensive search query to get a broad overview of the following topic:

TOPIC: {topic}

The query should be optimized for a search engine and help us understand:
- What this topic fundamentally is
- Key components, concepts, or dimensions
- Current state and recent developments
- Why it matters or its significance
- Major applications or implications

Requirements:
- Single query only (not multiple queries)
- Specific enough to get detailed results
- Broad enough to cover the full scope
- Natural language, optimized for search
- No more than 20 words

Return ONLY the query text, nothing else."""

# Import the EXACT prompt from PROMPTS.md Section 3.1
CONTEXT_EXTRACTION_PROMPT = """Analyze the following research overview and extract key contextual information.

ORIGINAL TOPIC: {topic}

OVERVIEW RESULT:
{overview_result}

TASK:
Extract and structure the following information from the overview:

1. Key Subtopics: 3-7 main areas or dimensions of this topic
2. Key Entities: 5-15 important organizations, people, technologies, or products
3. Terminology: 5-15 important technical terms or jargon
4. Research Angles: 3-7 different perspectives or approaches to study this topic

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "key_subtopics": ["subtopic1", "subtopic2", ...],
  "key_entities": ["entity1", "entity2", ...],
  "terminology": ["term1", "term2", ...],
  "research_angles": ["angle1", "angle2", ...]
}}

Requirements:
- Be specific and concrete
- Extract only information explicitly present or strongly implied
- Prioritize the most important/relevant items
- Use concise phrases (2-5 words each)

Return ONLY the JSON object, no additional text."""


async def generate_overview_query(topic: str) -> str:
    """Generate a single overview query using Claude.

    Args:
        topic: Research topic

    Returns:
        Overview query string
    """
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    message = client.messages.create(
        model=config.query_model,
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": OVERVIEW_QUERY_PROMPT.format(topic=topic)
        }]
    )

    return message.content[0].text.strip()


async def extract_context(topic: str, overview_result: str) -> dict:
    """Extract structured context from overview result.

    Args:
        topic: Original topic
        overview_result: Search result text

    Returns:
        Dictionary with extracted context
    """
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    message = client.messages.create(
        model=config.query_model,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": CONTEXT_EXTRACTION_PROMPT.format(
                topic=topic,
                overview_result=overview_result
            )
        }]
    )

    response_text = message.content[0].text.strip()

    # Parse JSON response
    # Handle cases where Claude wraps JSON in markdown code blocks
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    return json.loads(response_text)


async def reconnaissance(topic: str) -> ReconnaissanceContext:
    """Execute Phase 1: Reconnaissance.

    Args:
        topic: Research topic

    Returns:
        ReconnaissanceContext with overview and extracted insights
    """
    logger.info(f"Phase 1: Starting reconnaissance for '{topic}'")

    # Step 1: Generate overview query
    logger.info("Generating overview query...")
    overview_query = await generate_overview_query(topic)
    logger.info(f"Overview query: {overview_query}")

    # Step 2: Execute the search
    logger.info("Executing overview search...")
    try:
        async with aiohttp.ClientSession() as session:
            search_result = await search_single(overview_query, session)

        if not search_result.success:
            raise Exception(f"Reconnaissance search failed: {search_result.error_message}")
    except Exception as e:
        logger.error(f"Search failed after retries: {e}")
        raise Exception(f"Reconnaissance search failed: {str(e)}")

    overview_result = search_result.response_text
    logger.info(f"Overview result received ({len(overview_result)} chars)")

    # Step 3: Extract context
    logger.info("Extracting context from overview...")
    context_data = await extract_context(topic, overview_result)

    # Step 4: Create ReconnaissanceContext
    recon_context = ReconnaissanceContext(
        original_topic=topic,
        overview_query=overview_query,
        overview_result=overview_result,
        key_subtopics=context_data.get("key_subtopics", []),
        key_entities=context_data.get("key_entities", []),
        terminology=context_data.get("terminology", []),
        research_angles=context_data.get("research_angles", []),
        timestamp=datetime.now()
    )

    logger.info("Reconnaissance complete!")
    logger.info(f"Found {len(recon_context.key_subtopics)} subtopics, "
                f"{len(recon_context.key_entities)} entities")

    return recon_context
