"""Report synthesis using Claude Sonnet."""

import anthropic
import logging
from datetime import datetime

from .config import config
from .models import AggregatedResearch

logger = logging.getLogger(__name__)

# Import the EXACT prompt from PROMPTS.md Section 4.1
SYNTHESIS_PROMPT = """You are an expert research analyst creating an ultra-high-signal report.

RESEARCH TOPIC: {topic}

INITIAL RECONNAISSANCE:
{reconnaissance_summary}

DEEP RESEARCH RESULTS:
You conducted {total_queries} searches across multiple categories. Here are the aggregated findings:

{aggregated_results_by_category}

ALL SOURCES:
{source_list}

TASK:
Create a comprehensive research report that synthesizes these findings into actionable insights.

REPORT STRUCTURE:

# {topic} - Research Report

**Research Date**: {date}
**Queries Executed**: {successful_count} successful, {failed_count} failed
**Total Sources**: {source_count}

## Executive Summary

Write 2-3 paragraphs that:
- Provide a clear overview of the topic
- Highlight the most important findings
- State key conclusions or implications
- Use concrete facts and specific examples

## Key Insights

List 5-10 of the MOST IMPORTANT insights discovered. Each should be:
- Actionable or significant
- Supported by the research
- Concise (1-2 sentences)
- Prioritized by importance

## Detailed Findings

Organize findings into 4-6 logical sections based on the research. For each section:
- Use clear, descriptive headers
- Synthesize information from multiple sources
- Include specific examples, data, or quotes where relevant
- Attribute information to sources naturally (not just listed at end)
- Focus on signal, not noise

## Key Challenges and Limitations

What are the main challenges, limitations, or criticisms identified in the research?

## Future Outlook

What trends, developments, or opportunities were identified?

## Sources

List all sources referenced, grouped by category or relevance.

---

CRITICAL REQUIREMENTS:
- Be concise - remove fluff and redundancy
- Prioritize signal over volume
- Use specific examples and data points
- Make it scannable with clear headers
- Attribute important claims to sources
- Focus on insights, not just information
- Write in clear, professional prose
- No jargon unless necessary (explain when used)

OUTPUT:
Return the complete report in Markdown format."""


def synthesize_report(aggregated: AggregatedResearch) -> str:
    """Generate final high-signal report.

    Args:
        aggregated: Aggregated research data

    Returns:
        Markdown formatted report
    """
    logger.info("Phase 3: Synthesizing final report")

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    # Format reconnaissance summary
    recon = aggregated.reconnaissance
    recon_summary = f"""Overview Query: {recon.overview_query}
Key Subtopics: {', '.join(recon.key_subtopics[:5])}
Key Entities: {', '.join(recon.key_entities[:10])}"""

    # Format results by category
    results_text = ""
    for category, results in aggregated.results_by_category.items():
        results_text += f"\n### {category.upper()} ({len(results)} results)\n\n"
        for i, result in enumerate(results[:10], 1):  # Limit to 10 per category
            results_text += f"{i}. {result.response_text[:500]}...\n\n"

    # Format sources
    source_list = "\n".join(f"- {source}" for source in aggregated.all_sources[:50])

    # Build prompt
    prompt = SYNTHESIS_PROMPT.format(
        topic=aggregated.topic,
        reconnaissance_summary=recon_summary,
        total_queries=aggregated.total_queries,
        aggregated_results_by_category=results_text[:15000],  # Truncate if needed
        source_list=source_list,
        date=datetime.now().strftime("%Y-%m-%d"),
        successful_count=aggregated.successful_queries,
        failed_count=aggregated.failed_queries,
        source_count=len(aggregated.all_sources)
    )

    logger.info("Calling Claude Sonnet for synthesis...")

    # Call Claude Sonnet
    message = client.messages.create(
        model=config.synthesis_model,
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    report = message.content[0].text.strip()

    logger.info(f"Report generated ({len(report)} chars)")

    return report
