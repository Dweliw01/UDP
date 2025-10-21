"""Query generation for deep research phase."""

import anthropic
import json
import logging
from typing import List
from collections import Counter

from .config import config
from .models import ReconnaissanceContext, SearchQuery

logger = logging.getLogger(__name__)

# Import the EXACT prompt from PROMPTS.md Section 2.1
DEEP_QUERY_GENERATION_PROMPT = """You are a research strategist generating search queries for ultra-deep research.

ORIGINAL TOPIC: {topic}

RECONNAISSANCE OVERVIEW:
{overview_result}

KEY CONTEXT FROM INITIAL RESEARCH:
- Subtopics: {subtopics}
- Key Entities: {entities}
- Terminology: {terminology}
- Research Angles: {research_angles}

TASK:
Generate exactly {num_queries} diverse, specific search queries to comprehensively research this topic.

DISTRIBUTION REQUIREMENTS:
- 20% Foundational queries (what, why, history, core concepts)
- 15% Technical queries (how it works, mechanisms, architecture)
- 15% Application queries (use cases, implementations, real-world examples)
- 15% Comparative queries (vs alternatives, comparisons, trade-offs)
- 15% Critical queries (challenges, limitations, criticisms, debates)
- 10% Data-driven queries (statistics, studies, benchmarks, metrics)
- 10% Future-oriented queries (trends, predictions, roadmaps, opportunities)

QUERY REQUIREMENTS:
- Each query must be specific and answerable
- Cover different aspects mentioned in the overview
- Avoid redundancy with other queries
- Range from beginner to expert level
- Optimized for search engines (natural language)
- 5-25 words per query

OUTPUT FORMAT:
Return a JSON array of objects with this exact structure:
[
  {{
    "query": "specific search query text here",
    "category": "foundational|technical|application|comparative|critical|data|future"
  }},
  ...
]

Return ONLY the JSON array, no additional text or explanation."""


def generate_queries(
    topic: str,
    recon_context: ReconnaissanceContext,
    num_queries: int = 100
) -> List[SearchQuery]:
    """Generate diverse, targeted queries based on reconnaissance.

    Args:
        topic: Research topic
        recon_context: Context from reconnaissance phase
        num_queries: Number of queries to generate

    Returns:
        List of SearchQuery objects
    """
    logger.info(f"Generating {num_queries} queries for '{topic}'")

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    # Format the prompt
    prompt = DEEP_QUERY_GENERATION_PROMPT.format(
        topic=topic,
        overview_result=recon_context.overview_result[:2000],  # Truncate if too long
        subtopics=", ".join(recon_context.key_subtopics),
        entities=", ".join(recon_context.key_entities),
        terminology=", ".join(recon_context.terminology),
        research_angles=", ".join(recon_context.research_angles),
        num_queries=num_queries
    )

    # Call Claude
    message = client.messages.create(
        model=config.query_model,
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    response_text = message.content[0].text.strip()

    # Parse JSON response (handle markdown wrapping)
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    try:
        queries_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse query JSON: {e}")
        logger.error(f"Response was: {response_text[:500]}")
        raise

    # Convert to SearchQuery objects
    queries = [
        SearchQuery(
            query_text=q["query"],
            category=q["category"],
            priority=1
        )
        for q in queries_data
    ]

    logger.info(f"Generated {len(queries)} queries")

    # Log category distribution
    category_counts = Counter(q.category for q in queries)
    logger.info(f"Category distribution: {dict(category_counts)}")

    return queries
