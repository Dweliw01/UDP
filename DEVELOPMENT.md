# Development Guide

Guide for developers working on Ultra Deep Research.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- API keys (see [API_SETUP.md](API_SETUP.md))

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ultra-deep-research.git
cd ultra-deep-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Verify setup
python scripts/verify_setup.py
```

## Project Structure

```
ultra-deep-research/
├── src/                      # Main source code
│   ├── __init__.py
│   ├── cli.py               # CLI entry point
│   ├── reconnaissance.py    # Phase 1: Context gathering
│   ├── query_generator.py   # Phase 2: Query generation
│   ├── searcher.py          # Async search execution
│   ├── aggregator.py        # Result aggregation
│   ├── synthesizer.py       # Phase 3: Report generation
│   ├── config.py            # Configuration management
│   └── models.py            # Data models
│
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data
│
├── scripts/                  # Utility scripts
│   ├── verify_setup.py      # Setup verification
│   └── benchmark.py         # Performance benchmarking
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md      # Architecture details
│   ├── PROMPTS.md           # LLM prompt templates
│   └── API_SETUP.md         # API setup guide
│
├── examples/                 # Example outputs
│   ├── sample_queries.json
│   ├── sample_context.json
│   └── sample_report.md
│
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── .env.example             # Environment template
├── .gitignore
├── README.md
└── setup.py                 # Package setup
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Code

Follow the coding standards (see below).

### 3. Write Tests

```bash
# Run specific test
pytest tests/unit/test_query_generator.py

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### 4. Run Linters and Formatters

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Or run all at once
./scripts/lint.sh
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

```python
# Use type hints
def generate_queries(topic: str, num: int) -> List[SearchQuery]:
    pass

# Use docstrings (Google style)
def search_single(query: str) -> SearchResult:
    """Execute a single search query.
    
    Args:
        query: The search query string
        
    Returns:
        SearchResult object containing the response
        
    Raises:
        SearchError: If the search fails after retries
    """
    pass

# Use dataclasses for data models
from dataclasses import dataclass

@dataclass
class SearchQuery:
    query_text: str
    category: str
    priority: int = 1
```

### Async Code

```python
# Always use async/await for I/O operations
async def search_batch(queries: List[str]) -> List[SearchResult]:
    async with aiohttp.ClientSession() as session:
        tasks = [search_single(q, session) for q in queries]
        return await asyncio.gather(*tasks)

# Use proper error handling
try:
    result = await search_single(query)
except SearchError as e:
    logger.error(f"Search failed: {e}")
    # Handle gracefully
```

### Error Handling

```python
# Define custom exceptions
class UDRError(Exception):
    """Base exception for UDR"""
    pass

class SearchError(UDRError):
    """Search-related errors"""
    pass

# Use proper logging
import logging
logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

## Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
# tests/unit/test_query_generator.py
import pytest
from src.query_generator import generate_queries
from src.models import ReconnaissanceContext

def test_generate_queries_returns_correct_count():
    context = ReconnaissanceContext(
        original_topic="test",
        overview_query="test query",
        overview_result="test result",
        key_subtopics=["sub1"],
        key_entities=["entity1"],
        terminology=["term1"],
        research_angles=["angle1"]
    )
    
    queries = generate_queries("test topic", context, num_queries=50)
    assert len(queries) == 50

def test_generate_queries_has_diverse_categories():
    # Test that queries cover multiple categories
    pass
```

### Integration Tests

Test components working together:

```python
# tests/integration/test_full_pipeline.py
import pytest
from src.cli import run_research

@pytest.mark.asyncio
async def test_full_research_pipeline():
    """Test the complete research pipeline end-to-end"""
    # This actually calls APIs - use sparingly
    result = await run_research("test topic", num_queries=5)
    assert result.report is not None
    assert len(result.sources) > 0
```

### Test Fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_context():
    return ReconnaissanceContext(
        original_topic="quantum computing",
        overview_query="what is quantum computing",
        overview_result="Quantum computing is...",
        key_subtopics=["qubits", "algorithms"],
        key_entities=["IBM", "Google"],
        terminology=["superposition", "entanglement"],
        research_angles=["hardware", "applications"]
    )

@pytest.fixture
def mock_search_result():
    return SearchResult(
        query="test query",
        response_text="test response",
        sources=["source1.com"],
        timestamp=datetime.now(),
        category="technical",
        success=True
    )
```

### Mocking API Calls

```python
# tests/unit/test_searcher.py
import pytest
from unittest.mock import AsyncMock, patch
from src.searcher import search_single

@pytest.mark.asyncio
async def test_search_single_with_mock():
    with patch('aiohttp.ClientSession') as mock_session:
        # Mock the API response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"result": "test"}
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        
        result = await search_single("test query")
        assert result.success is True
```

## Debugging

### Enable Debug Logging

```bash
# Via CLI
udr "your topic" --debug

# Or set in .env
LOG_LEVEL=DEBUG
```

### Use Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use modern breakpoint()
breakpoint()
```

### Async Debugging

```python
# For async code
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # Windows
asyncio.run(your_async_function(), debug=True)
```

## Performance Optimization

### Profiling

```python
# Profile specific function
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = run_research("topic")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Async Performance

```python
# Measure async operations
import time

start = time.perf_counter()
results = await search_batch(queries)
elapsed = time.perf_counter() - start
print(f"Batch search took {elapsed:.2f}s")
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with profiling
python -m memory_profiler src/cli.py "topic"
```

## Adding New Features

### Example: Adding a New Search Provider

1. **Create the provider module**:
```python
# src/providers/new_provider.py
from abc import ABC, abstractmethod

class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> SearchResult:
        pass

class NewProvider(SearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str) -> SearchResult:
        # Implementation
        pass
```

2. **Update configuration**:
```python
# src/config.py
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "perplexity")
```

3. **Update searcher to use provider**:
```python
# src/searcher.py
def get_search_provider() -> SearchProvider:
    if config.SEARCH_PROVIDER == "perplexity":
        return PerplexityProvider(config.PERPLEXITY_API_KEY)
    elif config.SEARCH_PROVIDER == "new_provider":
        return NewProvider(config.NEW_PROVIDER_API_KEY)
```

4. **Add tests**:
```python
# tests/unit/test_new_provider.py
def test_new_provider_search():
    provider = NewProvider("test-key")
    result = await provider.search("test query")
    assert result.success
```

5. **Update documentation**:
- Add to README.md
- Update API_SETUP.md
- Add to ARCHITECTURE.md

## Common Tasks

### Running the CLI Locally

```bash
# From project root
python -m src.cli "your topic"

# Or install in editable mode
pip install -e .
udr "your topic"
```

### Updating Dependencies

```bash
# Update a specific package
pip install --upgrade anthropic

# Update all packages
pip install --upgrade -r requirements.txt

# Freeze current versions
pip freeze > requirements.txt
```

### Generating Documentation

```bash
# Install documentation tools
pip install sphinx sphinx-rtd-theme

# Generate docs
cd docs
make html

# View docs
open _build/html/index.html
```

## Troubleshooting

### Import Errors

```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or use editable install
pip install -e .
```

### Async Event Loop Issues

```python
# If you get "Event loop is closed" errors
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### API Rate Limiting

```python
# Reduce concurrency in config
MAX_CONCURRENT_SEARCHES = 5

# Add longer delays
RETRY_DELAY = 2.0
```

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `setup.py` and `src/__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release
6. Publish to PyPI (if applicable)

## Resources

### Documentation
- [Anthropic API Docs](https://docs.anthropic.com)
- [Perplexity API Docs](https://docs.perplexity.ai)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

### Tools
- [Black](https://black.readthedocs.io/) - Code formatter
- [mypy](https://mypy.readthedocs.io/) - Type checker
- [pytest](https://docs.pytest.org/) - Testing framework

### Learning
- [Python Async/Await](https://realpython.com/async-io-python/)
- [CLI Development with Click](https://click.palletsprojects.com/)
- [Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Issues**: Open a GitHub issue
- **Discussions**: GitHub Discussions
- **Security**: See SECURITY.md

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX
