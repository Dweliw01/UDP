# IMPLEMENTATION_GUIDE.md - Instructions for Claude Code

## 🎯 Mission

Implement **Ultra Deep Research (UDR)** - a CLI tool that performs ultra-deep research on any topic using a two-phase AI-powered approach: reconnaissance → deep research → synthesis.

## 📚 Required Reading (In Order)

Before starting implementation, you MUST read these documentation files in this order:

1. **README.md** - Understand what we're building and why
2. **ARCHITECTURE.md** - Understand the system design and components
3. **PROMPTS.md** - Critical for LLM interactions (copy these prompts exactly)
4. **API_SETUP.md** - Understand API requirements
5. **DEVELOPMENT.md** - Follow coding standards and patterns

## 🏗️ Implementation Phases

### Phase 0: Project Setup (30 minutes)

**Objective**: Set up the project structure and core infrastructure

**Tasks**:
- [ ] Create project directory structure as specified in ARCHITECTURE.md
- [ ] Set up `src/` directory with all module files
- [ ] Create `__init__.py` files for proper package structure
- [ ] Copy `.env.example` to `.env` (user will add keys later)
- [ ] Create empty test directory structure
- [ ] Set up logging configuration

**Files to Create**:
```
ultra-deep-research/
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── reconnaissance.py
│   ├── query_generator.py
│   ├── searcher.py
│   ├── aggregator.py
│   ├── synthesizer.py
│   ├── config.py
│   └── models.py
├── tests/
│   ├── __init__.py
│   └── test_basic.py
├── .gitignore
└── setup.py
```

**Success Criteria**:
- All directories and empty files exist
- Package structure is importable
- No import errors when running `python -c "import src"`

---

### Phase 1: Configuration & Models (30 minutes)

**Objective**: Implement configuration management and data models

#### Task 1.1: Create Data Models (`src/models.py`)

Implement these dataclasses (from ARCHITECTURE.md):

```python
@dataclass
class ReconnaissanceContext:
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
    query_text: str
    category: str
    priority: int = 1

@dataclass
class SearchResult:
    query: str
    response_text: str
    sources: List[str]
    timestamp: datetime
    category: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class AggregatedResearch:
    topic: str
    reconnaissance: ReconnaissanceContext
    results_by_category: Dict[str, List[SearchResult]]
    all_sources: List[str]
    total_queries: int
    successful_queries: int
    failed_queries: int
    timestamp: datetime
```

**Checklist**:
- [ ] All dataclasses implemented with correct fields
- [ ] Type hints are complete and correct
- [ ] Default values match the spec
- [ ] Import statements are correct (datetime, typing, dataclasses)

#### Task 1.2: Create Configuration (`src/config.py`)

Implement configuration management exactly as shown in ARCHITECTURE.md Section 7:

```python
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # Model Configuration
    query_model: str = "claude-haiku-4.5"
    synthesis_model: str = "claude-sonnet-4.5"
    
    # Search Configuration
    max_concurrent_searches: int = 15
    search_timeout: int = 30
    retry_attempts: int = 3
    
    # Query Configuration
    default_num_queries: int = 100
    
    # Output Configuration
    default_output_file: str = "research_report.md"
    
    def validate(self) -> bool:
        """Validate that required config is present."""
        return bool(self.anthropic_api_key and self.perplexity_api_key)

config = Config()
```

**Checklist**:
- [ ] Config class matches specification exactly
- [ ] Environment variables are loaded with python-dotenv
- [ ] validate() method works correctly
- [ ] Global config instance is created

**Success Criteria**:
- Running `python -c "from src.config import config; print(config)"` works
- Running `python -c "from src.models import *"` imports without errors

---

### Phase 2: Searcher Module (1 hour)

**Objective**: Implement async search functionality with Perplexity API

#### Task 2.1: Implement Basic Search (`src/searcher.py`)

Follow ARCHITECTURE.md Section 4 for specifications.

**Implementation Requirements**:

```python
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
    """Exception raised for search failures"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def search_single(query: str, session: aiohttp.ClientSession) -> SearchResult:
    """Execute a single search query via Perplexity API.
    
    Args:
        query: Search query string
        session: aiohttp ClientSession
        
    Returns:
        SearchResult object
        
    Raises:
        SearchError: If search fails after retries
    """
    # TODO: Implement Perplexity API call
    # Use config.perplexity_api_key
    # Handle errors gracefully
    # Return SearchResult with success=True/False
    pass

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
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_search(query: SearchQuery, session: aiohttp.ClientSession):
        async with semaphore:
            try:
                return await search_single(query.query_text, session)
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
        return await asyncio.gather(*tasks)
```

**Checklist**:
- [ ] search_single() implemented with Perplexity API integration
- [ ] Retry logic using tenacity is working
- [ ] search_batch() uses semaphore for concurrency control
- [ ] Error handling returns SearchResult with success=False
- [ ] Logging is implemented
- [ ] Type hints are complete

**CRITICAL NOTE**: You'll need to research the actual Perplexity API endpoint and request format. Check their documentation at https://docs.perplexity.ai

**Success Criteria**:
- Can execute a single search (with valid API key)
- Can execute batch searches with controlled concurrency
- Failed searches don't crash, return error SearchResult
- Semaphore limits concurrent requests correctly

---

### Phase 3: Reconnaissance Module (1 hour)

**Objective**: Implement Phase 1 - Initial context gathering

#### Task 3.1: Implement Reconnaissance (`src/reconnaissance.py`)

Follow ARCHITECTURE.md Section 2 and PROMPTS.md Section 1 for specifications.

**Implementation Requirements**:

```python
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
OVERVIEW_QUERY_PROMPT = """
Generate ONE comprehensive search query to get a broad overview of the following topic:

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

Return ONLY the query text, nothing else.
"""

# Import the EXACT prompt from PROMPTS.md Section 3.1
CONTEXT_EXTRACTION_PROMPT = """
Analyze the following research overview and extract key contextual information.

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

Return ONLY the JSON object, no additional text.
"""

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
    async with aiohttp.ClientSession() as session:
        search_result = await search_single(overview_query, session)
    
    if not search_result.success:
        raise Exception(f"Reconnaissance search failed: {search_result.error_message}")
    
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
```

**Checklist**:
- [ ] PROMPTS copied EXACTLY from PROMPTS.md (do not modify)
- [ ] generate_overview_query() calls Claude API correctly
- [ ] extract_context() parses JSON correctly (handles markdown wrapping)
- [ ] reconnaissance() orchestrates all steps
- [ ] Error handling for API failures
- [ ] Logging at each step
- [ ] Returns proper ReconnaissanceContext

**Success Criteria**:
- Can generate an overview query for a test topic
- Can execute the search and get results
- Can extract structured context from results
- Returns complete ReconnaissanceContext object

---

### Phase 4: Query Generator (1 hour)

**Objective**: Generate 100+ diverse queries based on reconnaissance context

#### Task 4.1: Implement Query Generator (`src/query_generator.py`)

Follow ARCHITECTURE.md Section 3 and PROMPTS.md Section 2.1 for specifications.

**Implementation Requirements**:

```python
import anthropic
import json
import logging
from typing import List

from .config import config
from .models import ReconnaissanceContext, SearchQuery

logger = logging.getLogger(__name__)

# Import the EXACT prompt from PROMPTS.md Section 2.1
DEEP_QUERY_GENERATION_PROMPT = """
You are a research strategist generating search queries for ultra-deep research.

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

Return ONLY the JSON array, no additional text or explanation.
"""

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
    from collections import Counter
    category_counts = Counter(q.category for q in queries)
    logger.info(f"Category distribution: {dict(category_counts)}")
    
    return queries
```

**Checklist**:
- [ ] PROMPT copied EXACTLY from PROMPTS.md
- [ ] generate_queries() calls Claude API correctly
- [ ] JSON parsing handles markdown wrapping
- [ ] Returns List[SearchQuery] objects
- [ ] Logging shows progress and category distribution
- [ ] Error handling for JSON parsing failures

**Success Criteria**:
- Generates exactly the requested number of queries
- Queries are diverse across categories
- Each query has valid category field
- No duplicate queries

---

### Phase 5: Aggregator (45 minutes)

**Objective**: Collect and structure search results

#### Task 5.1: Implement Aggregator (`src/aggregator.py`)

Follow ARCHITECTURE.md Section 5 for specifications.

**Implementation Requirements**:

```python
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
```

**Checklist**:
- [ ] Filters successful vs failed results
- [ ] Groups results by category
- [ ] Collects unique sources
- [ ] Returns AggregatedResearch object
- [ ] Logging shows summary statistics

**Success Criteria**:
- Correctly separates successful/failed results
- Groups by category properly
- No duplicate sources in all_sources list

---

### Phase 6: Synthesizer (1 hour)

**Objective**: Generate final report using Sonnet

#### Task 6.1: Implement Synthesizer (`src/synthesizer.py`)

Follow ARCHITECTURE.md Section 6 and PROMPTS.md Section 4.1 for specifications.

**Implementation Requirements**:

```python
import anthropic
import logging
from datetime import datetime

from .config import config
from .models import AggregatedResearch

logger = logging.getLogger(__name__)

# Import the EXACT prompt from PROMPTS.md Section 4.1
SYNTHESIS_PROMPT = """
You are an expert research analyst creating an ultra-high-signal report.

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
Return the complete report in Markdown format.
"""

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
    recon_summary = f"""
Overview Query: {recon.overview_query}
Key Subtopics: {', '.join(recon.key_subtopics[:5])}
Key Entities: {', '.join(recon.key_entities[:10])}
"""
    
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
```

**Checklist**:
- [ ] PROMPT copied EXACTLY from PROMPTS.md
- [ ] Formats reconnaissance summary correctly
- [ ] Formats results by category
- [ ] Truncates long content appropriately
- [ ] Uses Sonnet model (not Haiku)
- [ ] Returns markdown formatted report

**Success Criteria**:
- Generates well-structured markdown report
- Report includes all required sections
- Report is concise and high-signal

---

### Phase 7: CLI Implementation (1 hour)

**Objective**: Create command-line interface that orchestrates everything

#### Task 7.1: Implement CLI (`src/cli.py`)

Follow ARCHITECTURE.md Section 1 for specifications.

**Implementation Requirements**:

```python
import click
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from .config import config
from .reconnaissance import reconnaissance
from .query_generator import generate_queries
from .searcher import search_batch
from .aggregator import aggregate_results
from .synthesizer import synthesize_report

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
        output_path.write_text(result)
        
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
```

**Checklist**:
- [ ] Uses click for CLI framework
- [ ] Validates API keys before starting
- [ ] Shows progress messages for each phase
- [ ] Handles errors gracefully
- [ ] Saves report to specified output file
- [ ] Returns proper exit codes

**Success Criteria**:
- Can run from command line: `python -m src.cli "test topic"`
- Shows clear progress messages
- Saves report to file
- Handles missing API keys gracefully

---

### Phase 8: Testing & Refinement (1 hour)

**Objective**: Test the complete system and fix issues

#### Task 8.1: Create Basic Tests

```python
# tests/test_basic.py
import pytest
from src.models import SearchQuery, ReconnaissanceContext

def test_search_query_creation():
    query = SearchQuery(
        query_text="test query",
        category="foundational"
    )
    assert query.query_text == "test query"
    assert query.category == "foundational"
    assert query.priority == 1

def test_reconnaissance_context_creation():
    context = ReconnaissanceContext(
        original_topic="test",
        overview_query="test query",
        overview_result="test result",
        key_subtopics=["sub1"],
        key_entities=["entity1"],
        terminology=["term1"],
        research_angles=["angle1"],
        timestamp=datetime.now()
    )
    assert context.original_topic == "test"
    assert len(context.key_subtopics) == 1
```

#### Task 8.2: Manual Testing Checklist

- [ ] Test with a simple topic (e.g., "Python programming")
- [ ] Test with a complex topic (e.g., "quantum computing applications in drug discovery")
- [ ] Test with num_queries=10 for faster testing
- [ ] Verify all phases complete successfully
- [ ] Check report quality and structure
- [ ] Test with missing API keys (should fail gracefully)
- [ ] Test with invalid topic (empty string, special characters)

#### Task 8.3: Known Issues to Fix

Common issues and how to fix them:

1. **JSON parsing fails**: Make sure to handle markdown code blocks in responses
2. **Rate limiting**: Reduce MAX_CONCURRENT_SEARCHES if needed
3. **Timeout errors**: Increase SEARCH_TIMEOUT in config
4. **Empty results**: Check Perplexity API integration
5. **Report too long**: Add truncation logic in synthesizer

---

## 🎯 Success Criteria for Complete Implementation

The implementation is successful when:

### Functional Requirements
- [ ] Can execute full research pipeline from CLI
- [ ] Generates 100+ diverse queries
- [ ] Executes searches in parallel with concurrency control
- [ ] Produces well-structured markdown report
- [ ] Handles errors gracefully (doesn't crash)

### Quality Requirements
- [ ] Code follows Python best practices (type hints, docstrings)
- [ ] Logging provides visibility into each phase
- [ ] Error messages are helpful to users
- [ ] Configuration is properly managed via .env
- [ ] All prompts are copied exactly from PROMPTS.md

### Testing Requirements
- [ ] Basic unit tests pass
- [ ] Can successfully research at least 3 different topics
- [ ] Total execution time is under 2 minutes for 100 queries
- [ ] Report quality is high (readable, actionable insights)

---

## 🚨 Critical Implementation Notes

### DO's ✅
- ✅ **Copy prompts EXACTLY from PROMPTS.md** - Do not modify the prompts
- ✅ **Follow data models exactly** - Use the dataclasses as specified
- ✅ **Implement async properly** - Use asyncio and aiohttp correctly
- ✅ **Add comprehensive logging** - Every major step should log
- ✅ **Handle errors gracefully** - Don't let exceptions crash the program
- ✅ **Test incrementally** - Test each phase before moving to next

### DON'Ts ❌
- ❌ **Don't modify prompts** - They're carefully crafted
- ❌ **Don't skip error handling** - It's critical for reliability
- ❌ **Don't hardcode API keys** - Always use environment variables
- ❌ **Don't ignore rate limits** - Use semaphore and retry logic
- ❌ **Don't skip logging** - It's essential for debugging

---

## 📝 Implementation Checklist

Use this to track your progress:

### Setup Phase
- [ ] Project structure created
- [ ] All module files exist
- [ ] requirements.txt dependencies installable
- [ ] .env.example present

### Core Implementation
- [ ] models.py - All dataclasses implemented
- [ ] config.py - Configuration management working
- [ ] searcher.py - Async search with Perplexity API
- [ ] reconnaissance.py - Phase 1 complete
- [ ] query_generator.py - Query generation working
- [ ] aggregator.py - Result aggregation working
- [ ] synthesizer.py - Report generation working
- [ ] cli.py - CLI orchestration complete

### Testing
- [ ] Basic unit tests written
- [ ] Manual testing completed
- [ ] At least 3 successful research runs
- [ ] Error handling verified

### Documentation
- [ ] Code has docstrings
- [ ] Comments explain complex logic
- [ ] README.md updated with usage examples

---

## 🆘 If You Get Stuck

### Common Issues

**Issue**: "Module not found" errors
**Solution**: Ensure you're running from project root and using `python -m src.cli`

**Issue**: Perplexity API not working
**Solution**: Research the current Perplexity API documentation at https://docs.perplexity.ai for the correct endpoint and request format

**Issue**: Rate limiting errors
**Solution**: Reduce MAX_CONCURRENT_SEARCHES to 5 and increase RETRY_DELAY

**Issue**: Claude API errors
**Solution**: Check that API key is correct and you have credits

**Issue**: Report quality is poor
**Solution**: Check that prompts are copied exactly from PROMPTS.md - do not modify them

### Getting Help

1. Review the relevant .md file for that component
2. Check ARCHITECTURE.md for design decisions
3. Look at DEVELOPMENT.md for coding patterns
4. Verify prompts match PROMPTS.md exactly

---

## 📦 Final Deliverables

When complete, the project should have:

1. **Working CLI tool** that can be run with `python -m src.cli "topic"`
2. **All source files** properly implemented
3. **Basic tests** in place
4. **Documentation** up to date
5. **Example output** from a successful research run

---

## 🎉 You're Ready!

You now have everything you need to implement Ultra Deep Research:

1. **Architecture** is designed (ARCHITECTURE.md)
2. **Prompts** are written (PROMPTS.md)
3. **API setup** is documented (API_SETUP.md)
4. **Implementation plan** is clear (this file)
5. **Coding standards** are defined (DEVELOPMENT.md)

**Estimated implementation time**: 6-8 hours for MVP

**Start with Phase 0 and work through sequentially. Test each phase before moving to the next.**

Good luck! 🚀
