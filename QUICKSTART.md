# Ultra Deep Research - Quick Start Guide

## Implementation Status: ✅ COMPLETE!

The Ultra Deep Research (UDR) project has been fully implemented and is ready to use!

## What Was Built

All 8 implementation phases are complete:

- ✅ **Phase 0**: Project structure created
- ✅ **Phase 1**: Data models and configuration implemented
- ✅ **Phase 2**: Async searcher with Perplexity API
- ✅ **Phase 3**: Reconnaissance module
- ✅ **Phase 4**: Query generator
- ✅ **Phase 5**: Result aggregator
- ✅ **Phase 6**: Report synthesizer
- ✅ **Phase 7**: CLI orchestration
- ✅ **Phase 8**: Tests, setup files, and documentation

## Project Structure

```
ultra-deep-research/
├── src/
│   ├── __init__.py           ✓ Created
│   ├── models.py             ✓ Created (data models)
│   ├── config.py             ✓ Created (configuration)
│   ├── searcher.py           ✓ Created (Perplexity API client)
│   ├── reconnaissance.py     ✓ Created (Phase 1: context gathering)
│   ├── query_generator.py    ✓ Created (Phase 2: query generation)
│   ├── aggregator.py         ✓ Created (result aggregation)
│   ├── synthesizer.py        ✓ Created (Phase 3: report synthesis)
│   └── cli.py                ✓ Created (CLI orchestration)
├── tests/
│   └── test_basic.py         ✓ Created (6 tests - all passing)
├── setup.py                  ✓ Created
├── .gitignore                ✓ Created
└── All documentation         ✓ Already present
```

## Next Steps to Get Started

### 1. Set Up Your API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the Package (Optional)

For easier usage, install in editable mode:

```bash
pip install -e .
```

This will create a `udr` command you can use from anywhere.

### 4. Run Your First Research!

**Option A: Using Python module**
```bash
python -m src.cli "artificial intelligence safety"
```

**Option B: Using installed command** (if you ran `pip install -e .`)
```bash
udr "artificial intelligence safety"
```

**With options:**
```bash
# Specify number of queries and output file
python -m src.cli "quantum computing" --num-queries 50 --output quantum_report.md

# Enable debug logging
python -m src.cli "climate change solutions" --debug
```

## Testing

Run the test suite to verify everything works:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src -v
```

All 6 basic tests should pass ✓

## Expected Behavior

When you run a research query, you'll see:

```
🔬 Ultra Deep Research: your topic
📊 Generating 100 queries

📍 Phase 1: Reconnaissance
   Found X subtopics, Y entities

🔍 Phase 2: Generating 100 queries
   Generated 100 queries

🌐 Phase 2: Executing searches
   Completed 95/100 searches

📊 Aggregating results
✍️  Phase 3: Synthesizing report

⏱️  Total time: 90.5s

✅ Research complete!
📄 Report saved to: research_report.md
```

## What Each Component Does

1. **reconnaissance.py**: Generates an overview query, searches, and extracts context
2. **query_generator.py**: Creates 100+ targeted queries based on context
3. **searcher.py**: Executes searches in parallel via Perplexity API
4. **aggregator.py**: Collects and organizes all results
5. **synthesizer.py**: Uses Claude Sonnet to generate final report
6. **cli.py**: Orchestrates the entire pipeline

## Configuration Options

You can customize behavior via environment variables in `.env`:

```env
# Model Selection
QUERY_MODEL=claude-haiku-4-20250514
SYNTHESIS_MODEL=claude-sonnet-4-20250514

# Performance Tuning
MAX_CONCURRENT_SEARCHES=15    # Reduce if hitting rate limits
SEARCH_TIMEOUT=30             # Increase if searches timeout
RETRY_ATTEMPTS=3

# Defaults
DEFAULT_NUM_QUERIES=100
DEFAULT_OUTPUT_FILE=research_report.md
```

## Troubleshooting

### "API keys not configured"
- Make sure you created `.env` file
- Check that API keys are set correctly
- Run: `python -c "from src.config import config; print(config.validate())"`

### Rate limiting errors
- Reduce `MAX_CONCURRENT_SEARCHES` in config.py or .env
- Add delays between requests

### Import errors
- Make sure you're in the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Search timeouts
- Increase `SEARCH_TIMEOUT` in config
- Check your internet connection

## Example Topics to Try

Start with these to test the system:

```bash
# Simple technical topic
python -m src.cli "Python async programming" --num-queries 20

# Complex research topic
python -m src.cli "quantum computing applications in drug discovery"

# Emerging topic
python -m src.cli "latest developments in AI reasoning models"

# Broad topic
python -m src.cli "climate change mitigation strategies"
```

## Performance Expectations

- **Phase 1 (Reconnaissance)**: ~10-15 seconds
- **Phase 2 (Deep Research)**: ~30-60 seconds for 100 queries
- **Phase 3 (Synthesis)**: ~10-20 seconds
- **Total**: ~60-90 seconds for a complete research cycle

## Cost Estimates

Per research session (100 queries):
- **Claude API**: ~$0.16-0.36
  - Reconnaissance: ~$0.01
  - Query generation: ~$0.05
  - Synthesis: ~$0.10-0.30
- **Perplexity API**: Check current pricing

## Next Steps

1. ✅ Set up API keys
2. ✅ Install dependencies
3. ✅ Run a test research query
4. ✅ Review the generated report
5. ✅ Adjust configuration as needed

## Documentation

For more details, see:
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design
- `API_SETUP.md` - API configuration details
- `DEVELOPMENT.md` - Development guidelines
- `PROMPTS.md` - LLM prompt templates

## Success!

You now have a fully functional AI-powered research tool! 🎉

The system will:
- Generate 100+ targeted research queries
- Execute them in parallel
- Aggregate and synthesize results
- Produce a high-signal markdown report

Happy researching! 🔬
