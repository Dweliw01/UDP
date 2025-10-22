"""Command-line interface for Ultra Deep Research."""

import click
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

from .config import config
from .reconnaissance import reconnaissance
from .query_generator import generate_queries
from .searcher import search_batch
from .aggregator import aggregate_results
from .synthesizer import synthesize_report

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.command()
@click.argument('topic')
@click.option('--num-queries', '-n', default=100, help='Number of queries to generate')
@click.option('--output', '-o', default='research_report.md', help='Output file path')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def research(topic: str, num_queries: int, output: str, debug: bool):
    """Conduct ultra-deep research on a topic."""

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate API keys
    if not config.validate():
        click.echo("❌ Error: API keys not configured", err=True)
        click.echo("Please set ANTHROPIC_API_KEY and PERPLEXITY_API_KEY in .env file")
        return 1

    click.echo(f"\n🔬 Ultra Deep Research: {topic}")
    click.echo(f"📊 Generating {num_queries} queries\n")

    try:
        # Run the research pipeline
        result = asyncio.run(run_research_pipeline(topic, num_queries))

        # Save report
        output_path = Path(output)
        output_path.write_text(result, encoding='utf-8')

        click.echo(f"\n✅ Research complete!")
        click.echo(f"📄 Report saved to: {output}")

        return 0

    except Exception as e:
        logger.exception("Research failed")
        click.echo(f"\n❌ Error: {e}", err=True)
        return 1


async def run_research_pipeline(topic: str, num_queries: int) -> str:
    """Execute the full research pipeline.

    Args:
        topic: Research topic
        num_queries: Number of queries to generate

    Returns:
        Final report markdown
    """
    start_time = datetime.now()

    # Phase 1: Reconnaissance
    click.echo("📍 Phase 1: Reconnaissance")
    recon_context = await reconnaissance(topic)
    click.echo(f"   Found {len(recon_context.key_subtopics)} subtopics, "
               f"{len(recon_context.key_entities)} entities\n")

    # Phase 2: Generate queries
    click.echo(f"🔍 Phase 2: Generating {num_queries} queries")
    queries = generate_queries(topic, recon_context, num_queries)
    click.echo(f"   Generated {len(queries)} queries\n")

    # Phase 2: Execute searches
    click.echo(f"🌐 Phase 2: Executing searches")
    results = await search_batch(queries)
    click.echo(f"   Completed {sum(1 for r in results if r.success)}/{len(results)} searches\n")

    # Aggregate results
    click.echo("📊 Aggregating results")
    aggregated = aggregate_results(topic, results, recon_context)

    # Phase 3: Synthesize report
    click.echo("✍️  Phase 3: Synthesizing report")
    report = synthesize_report(aggregated)

    elapsed = (datetime.now() - start_time).total_seconds()
    click.echo(f"\n⏱️  Total time: {elapsed:.1f}s")

    return report


def main():
    """Entry point for CLI."""
    research()


if __name__ == '__main__':
    main()
