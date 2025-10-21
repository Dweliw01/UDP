# Architecture Documentation

## Overview

Ultra Deep Research (UDR) is designed as a three-phase pipeline that progressively refines research from broad reconnaissance to deep analysis to synthesis.

## Design Principles

1. **Simplicity First**: MVP architecture with minimal abstractions
2. **Async by Default**: Parallel execution where possible
3. **Fail Gracefully**: Continue even with partial failures
4. **Progressive Enhancement**: Easy to add features later

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  (cli.py - User input, arg parsing, progress display)       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: RECONNAISSANCE                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ reconnaissance.py                                     │  │
│  │  - Generate 1 overview query (Haiku 4.5)            │  │
│  │  - Execute via Perplexity API                        │  │
│  │  - Extract context (subtopics, entities, angles)    │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ ReconnaissanceContext
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: DEEP RESEARCH                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ query_generator.py                                    │  │
│  │  - Generate 100+ queries with context (Haiku 4.5)   │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │ List[SearchQuery]                   │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ searcher.py (Async Batch Execution)                  │  │
│  │  - Semaphore-controlled concurrency                  │  │
│  │  - Retry logic with exponential backoff              │  │
│  │  - Progress tracking                                 │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │ List[SearchResult]                  │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ aggregator.py                                        │  │
│  │  - Deduplicate results                               │  │
│  │  - Group by category                                 │  │
│  │  - Track sources                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ AggregatedResearch
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 3: SYNTHESIS                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ synthesizer.py                                       │  │
│  │  - Format context for Sonnet 4.5                    │  │
│  │  - Generate structured report                        │  │
│  │  - Format as Markdown                                │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                   Final Report (.md)
```

## Component Details

### 1. CLI Layer (`cli.py`)

**Purpose**: Entry point for user interaction

**Technology**: `click` library

**Responsibilities**:
- Parse command-line arguments
- Validate input
- Orchestrate the three phases
- Display progress to user
- Handle errors gracefully

**Interface**:
```python
@click.command()
@click.argument('topic')
@click.option('--num-queries', default=100, help='Number of queries to generate')
@click.option('--output', '-o', default='report.md', help='Output file path')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def research(topic: str, num_queries: int, output: str, debug: bool):
    """Conduct ultra-deep research on a topic."""
    pass
```

### 2. Reconnaissance Module (`reconnaissance.py`)

**Purpose**: Phase 1 - Gather initial context

**Key Function**:
```python
async def reconnaissance(topic: str) -> ReconnaissanceContext:
    """
    Execute Phase 1: Single overview query to understand the topic.
    
    Returns:
        ReconnaissanceContext with overview and extracted insights
    """
    # 1. Generate overview query using Haiku
    # 2. Execute via Perplexity
    # 3. Parse and structure the response
    # 4. Return context object
```

**Data Model**:
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
```

**Dependencies**:
- Anthropic SDK (for Haiku)
- `searcher.py` (for Perplexity call)

### 3. Query Generator (`query_generator.py`)

**Purpose**: Generate 100+ targeted queries using reconnaissance context

**Key Function**:
```python
def generate_queries(
    topic: str,
    recon_context: ReconnaissanceContext,
    num_queries: int = 100
) -> List[SearchQuery]:
    """
    Generate diverse, targeted queries based on reconnaissance.
    
    Query categories:
    - Foundational (20%)
    - Technical (15%)
    - Application (15%)
    - Comparative (15%)
    - Critical (15%)
    - Data-driven (10%)
    - Future-oriented (10%)
    """
```

**Data Model**:
```python
@dataclass
class SearchQuery:
    query_text: str
    category: str  # e.g., "foundational", "technical", etc.
    priority: int = 1  # For future optimization
```

**Prompt Strategy**:
- Include full reconnaissance context
- Request specific distribution across categories
- Emphasize diversity and specificity
- Request JSON output for easy parsing

### 4. Searcher (`searcher.py`)

**Purpose**: Execute searches via Perplexity API with async control

**Key Functions**:
```python
async def search_single(query: str) -> SearchResult:
    """Execute a single search query (for reconnaissance)."""

async def search_batch(
    queries: List[SearchQuery],
    max_concurrent: int = 15
) -> List[SearchResult]:
    """Execute multiple queries with concurrency control."""
```

**Features**:
- **Semaphore**: Limit concurrent requests to avoid rate limits
- **Retry Logic**: Exponential backoff using `tenacity`
- **Progress Tracking**: Integration with `tqdm`
- **Error Handling**: Continue on failures, log errors

**Data Model**:
```python
@dataclass
class SearchResult:
    query: str
    response_text: str
    sources: List[str]
    timestamp: datetime
    category: str
    success: bool
    error_message: Optional[str] = None
```

**Configuration**:
```python
MAX_CONCURRENT_REQUESTS = 15
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0  # seconds
TIMEOUT = 30  # seconds
```

### 5. Aggregator (`aggregator.py`)

**Purpose**: Collect, deduplicate, and structure search results

**Key Function**:
```python
def aggregate_results(
    results: List[SearchResult],
    recon_context: ReconnaissanceContext
) -> AggregatedResearch:
    """
    Aggregate search results into structured format.
    
    Steps:
    1. Filter failed results
    2. Deduplicate near-identical results
    3. Group by category
    4. Extract and consolidate sources
    5. Calculate coverage metrics
    """
```

**Data Model**:
```python
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

**Deduplication Strategy** (MVP):
- Simple text similarity using basic hashing
- Remove results with >80% content overlap
- Keep the result with more sources

### 6. Synthesizer (`synthesizer.py`)

**Purpose**: Generate final report using Sonnet 4.5

**Key Function**:
```python
async def synthesize_report(
    aggregated: AggregatedResearch,
    output_format: str = "markdown"
) -> str:
    """
    Generate final high-signal report.
    
    Returns:
        Formatted markdown report
    """
```

**Report Structure**:
```markdown
# [Topic] - Research Report

**Generated**: [timestamp]
**Queries Executed**: X successful, Y failed

## Executive Summary
[2-3 paragraph overview]

## Key Insights
[5-10 bullet points of most important findings]

## Detailed Findings

### [Category 1]
[Synthesized insights from that category]

### [Category 2]
...

## Sources
[Consolidated list of all sources cited]

## Methodology
[Brief explanation of research process]
```

**Prompt Strategy**:
- Emphasize conciseness and signal
- Request specific structure
- Ask for source attribution
- Prioritize actionable insights

### 7. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Implementation**:
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

## Error Handling Strategy

### Graceful Degradation

1. **Reconnaissance Failure**: 
   - Retry up to 3 times
   - If still fails, proceed with topic only (no context)
   - Log warning

2. **Query Generation Failure**:
   - Retry with simplified prompt
   - Fall back to smaller number of queries
   - If total failure, abort with error message

3. **Search Failures**:
   - Continue with successful results
   - Log all failures
   - Include failure count in report
   - Minimum threshold: 50% success rate

4. **Synthesis Failure**:
   - Retry with truncated input
   - Fall back to simpler prompt
   - Last resort: Output raw aggregated data

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Module-specific loggers
recon_logger = logging.getLogger('reconnaissance')
search_logger = logging.getLogger('searcher')
synth_logger = logging.getLogger('synthesizer')
```

## Performance Considerations

### MVP Targets

- **Phase 1**: < 15 seconds
- **Phase 2**: < 60 seconds (100 queries)
- **Phase 3**: < 20 seconds
- **Total**: ~90 seconds for full research cycle

### Optimization Opportunities (Future)

1. **Caching**: Store successful queries and results
2. **Query Batching**: Group similar queries
3. **Incremental Results**: Stream results as they arrive
4. **Parallel Synthesis**: Generate sections concurrently
5. **Smart Retry**: Adjust retry strategy based on error type

## Testing Strategy

### Unit Tests
- Each module independently testable
- Mock API calls
- Test data models and transformations

### Integration Tests
- Test full pipeline with real APIs (using test topics)
- Verify output format
- Test error scenarios

### Manual Testing Topics
- Narrow technical topic: "Rust async runtime internals"
- Broad topic: "climate change"
- Ambiguous topic: "impact"
- Emerging topic: "recent AI developments"

## Future Enhancements

### Short Term
- [ ] Add result caching
- [ ] Improve deduplication algorithm
- [ ] Add more output formats (HTML, JSON)
- [ ] Better progress indicators

### Medium Term
- [ ] Query optimization based on result quality
- [ ] Support for multiple search APIs
- [ ] Interactive mode (user can guide research)
- [ ] Result visualization

### Long Term
- [ ] Web interface
- [ ] Collaborative research sessions
- [ ] Integration with note-taking tools
- [ ] Custom research templates

## Dependencies

### Core
```
anthropic>=0.18.0      # Claude API
aiohttp>=3.9.0         # Async HTTP
click>=8.1.0           # CLI framework
python-dotenv>=1.0.0   # Environment config
tqdm>=4.66.0           # Progress bars
tenacity>=8.2.0        # Retry logic
```

### Dev
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
mypy>=1.5.0
```

## Deployment

### Local Development
```bash
python -m src.cli "your topic"
```

### Installation
```bash
pip install -e .
```

### Docker (Future)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
ENTRYPOINT ["python", "-m", "src.cli"]
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: Design Phase
