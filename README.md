# Ultra Deep Research (UDR)

A CLI tool that deploys an "army of AI agents" to perform ultra-deep research on any topic using a two-phase approach: reconnaissance followed by parallel deep research.

## Overview

UDR uses AI reasoning models and search APIs to conduct comprehensive research that goes far beyond what a single search query can provide. It generates 100+ targeted search queries, executes them in parallel, and synthesizes the results into a high-signal report.

## Key Features

- **Two-Phase Research**: Initial reconnaissance to understand the topic, then deep parallel research
- **Intelligent Query Generation**: AI-generated queries tailored to your specific topic
- **Parallel Execution**: Asynchronous searches for speed and efficiency
- **High-Signal Output**: Concise, actionable reports with key insights

## How It Works

1. **Phase 1: Reconnaissance** (~10-15 seconds)
   - Generate one broad overview query using AI
   - Fetch initial context about the topic
   - Extract key subtopics, entities, and research angles

2. **Phase 2: Deep Research** (~30-60 seconds)
   - Generate 100+ targeted queries based on the context
   - Execute all queries in parallel via Perplexity API
   - Aggregate and deduplicate results

3. **Phase 3: Synthesis** (~10-20 seconds)
   - Send aggregated research to a powerful reasoning model
   - Generate a structured, high-signal report

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ultra-deep-research.git
cd ultra-deep-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your API keys (see API_SETUP.md)
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

```bash
# Basic usage
udr "artificial intelligence safety"

# With options
udr "quantum computing applications" --num-queries 150 --output my-report.md

# Specify output location
udr "climate change solutions" -o reports/climate.md
```

## Configuration

Edit `.env` file with your API credentials:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here

# Optional: Model configuration
QUERY_MODEL=claude-haiku-4.5
SYNTHESIS_MODEL=claude-sonnet-4.5
```

## Output Format

Reports are generated in Markdown format with the following structure:

- **Executive Summary**: 2-3 paragraph overview
- **Key Insights**: 5-10 most important findings
- **Detailed Findings**: Organized sections by topic
- **Sources**: Citations and references

## Project Structure

```
ultra-deep-research/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── reconnaissance.py   # Phase 1: Initial context gathering
│   ├── query_generator.py  # Phase 2: Generate deep queries
│   ├── searcher.py         # Async Perplexity API client
│   ├── aggregator.py       # Results collection and structuring
│   ├── synthesizer.py      # Final report generation
│   └── config.py           # Configuration management
├── tests/
├── docs/
│   ├── ARCHITECTURE.md     # Detailed architecture
│   ├── PROMPTS.md          # LLM prompt templates
│   └── API_SETUP.md        # API setup guide
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.9+
- Anthropic API key (for Claude)
- Perplexity API key (for search)

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with debug logging
udr "your topic" --debug
```

## Roadmap

- [ ] MVP Implementation
- [ ] Add caching layer for repeated queries
- [ ] Implement result deduplication
- [ ] Add support for multiple output formats (JSON, HTML)
- [ ] Web interface
- [ ] Support for additional search APIs
- [ ] Query optimization based on feedback

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details

## Support

- Documentation: See `docs/` folder
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/) for reasoning
- [Perplexity API](https://www.perplexity.ai/) for search
- Python asyncio for parallel execution

---

**Note**: This is an MVP. The architecture is intentionally minimal for fast iteration and learning.
