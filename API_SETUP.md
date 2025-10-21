# API Setup Guide

This guide will help you set up the required API credentials for Ultra Deep Research.

## Required APIs

UDR requires two API services:

1. **Anthropic API** - For Claude models (reasoning and synthesis)
2. **Perplexity API** - For web search

## Step-by-Step Setup

### 1. Anthropic API Setup

#### Create an Account

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for an account or log in
3. Navigate to API Keys section

#### Get Your API Key

1. Click "Create Key" or "Get API Key"
2. Copy your API key (starts with `sk-ant-`)
3. **Important**: Store this securely - you won't be able to see it again

#### Pricing Information

As of January 2025:
- **Claude Haiku 4.5**: ~$0.25 per million input tokens, ~$1.25 per million output tokens
- **Claude Sonnet 4.5**: ~$3 per million input tokens, ~$15 per million output tokens

**Estimated Cost per Research Session**:
- Phase 1 (Reconnaissance): ~$0.01
- Phase 2 (Query Generation): ~$0.05
- Phase 3 (Synthesis): ~$0.10-0.30
- **Total per research**: ~$0.16-0.36

#### Usage Limits

- Free tier: Check current Anthropic offerings
- Rate limits: Varies by tier (typically 50-100 requests/minute)

### 2. Perplexity API Setup

#### Create an Account

1. Go to [perplexity.ai](https://www.perplexity.ai)
2. Navigate to API access or [docs.perplexity.ai](https://docs.perplexity.ai)
3. Sign up for API access

#### Get Your API Key

1. Go to your account settings or API section
2. Generate a new API key
3. Copy your API key (format varies)
4. Store securely

#### Pricing Information

Check current Perplexity API pricing:
- Typically charged per search/query
- May have different tiers for different models

**Estimated Cost per Research Session**:
- Phase 1: 1 query
- Phase 2: 100+ queries
- **Total per research**: Depends on Perplexity pricing model

#### Usage Limits

- Rate limits: Check Perplexity documentation
- Concurrent requests: Adjust `max_concurrent` in config if you hit limits

### 3. Environment Configuration

#### Create `.env` File

In your project root directory, create a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

#### Add Your API Keys

```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Perplexity API Configuration
PERPLEXITY_API_KEY=your-perplexity-key-here

# Optional: Model Configuration (defaults shown)
QUERY_MODEL=claude-haiku-4.5
SYNTHESIS_MODEL=claude-sonnet-4.5

# Optional: Performance Configuration
MAX_CONCURRENT_SEARCHES=15
SEARCH_TIMEOUT=30
RETRY_ATTEMPTS=3

# Optional: Default Settings
DEFAULT_NUM_QUERIES=100
DEFAULT_OUTPUT_FILE=research_report.md
```

#### Secure Your Keys

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore

# Set proper permissions (Unix/Mac)
chmod 600 .env
```

### 4. Verify Setup

#### Test API Connections

Run the verification script:

```bash
python scripts/verify_api_setup.py
```

This will:
- Check if API keys are present
- Test connection to Anthropic API
- Test connection to Perplexity API
- Verify basic functionality

#### Manual Verification

Test Anthropic API:
```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-haiku-4.5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(message.content)
```

Test Perplexity API:
```python
import os
import aiohttp
import asyncio

async def test_perplexity():
    url = "https://api.perplexity.ai/chat/completions"  # Check actual endpoint
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "pplx-7b-online",  # Check current model names
        "messages": [{"role": "user", "content": "test"}]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            result = await response.json()
            print(result)

asyncio.run(test_perplexity())
```

## Troubleshooting

### Common Issues

#### "API Key Not Found"

**Problem**: Environment variables not loaded

**Solutions**:
```bash
# Check if .env file exists
ls -la .env

# Verify contents (without exposing keys)
grep "API_KEY" .env

# Ensure python-dotenv is installed
pip install python-dotenv

# Try loading manually
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Keys loaded' if os.getenv('ANTHROPIC_API_KEY') else 'Keys not found')"
```

#### "Authentication Failed" / 401 Error

**Problem**: Invalid API key

**Solutions**:
1. Double-check key was copied correctly (no extra spaces)
2. Verify key is active in the API provider's dashboard
3. Check if key has necessary permissions
4. Regenerate key if needed

#### Rate Limit Errors

**Problem**: Too many requests

**Solutions**:
```python
# In config.py, reduce concurrent requests
MAX_CONCURRENT_SEARCHES = 5  # Instead of 15

# Increase retry delay
RETRY_DELAY = 2.0  # Instead of 1.0
```

#### Timeout Errors

**Problem**: Searches taking too long

**Solutions**:
```python
# In config.py, increase timeout
SEARCH_TIMEOUT = 60  # Instead of 30
```

### Getting Help

1. **Anthropic Support**: [support.anthropic.com](https://support.anthropic.com)
2. **Perplexity Support**: Check their documentation
3. **Project Issues**: GitHub Issues

## Security Best Practices

### Do's ✅

- ✅ Store API keys in `.env` file
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in code
- ✅ Rotate keys periodically
- ✅ Use separate keys for dev/prod
- ✅ Set up usage alerts in provider dashboards

### Don'ts ❌

- ❌ Never commit API keys to version control
- ❌ Don't share keys in screenshots or logs
- ❌ Don't use production keys for testing
- ❌ Don't hardcode keys in source files
- ❌ Don't share `.env` files

### If Keys Are Exposed

1. **Immediately revoke** the compromised key
2. **Generate a new key** in the provider dashboard
3. **Update** your `.env` file
4. **Review** any unexpected usage in the provider's dashboard
5. **Report** to the provider if fraudulent usage occurred

## Cost Management

### Monitoring Usage

#### Anthropic Dashboard
1. Go to console.anthropic.com
2. Navigate to Usage or Billing
3. Set up usage alerts

#### Perplexity Dashboard
1. Check your Perplexity account
2. Monitor query usage
3. Set up alerts if available

### Setting Budget Limits

#### In Code (config.py):
```python
# Set maximum queries per research session
MAX_QUERIES_PER_SESSION = 100

# Set maximum retry attempts
MAX_RETRY_ATTEMPTS = 3

# Implement cost tracking
class CostTracker:
    def __init__(self):
        self.total_cost = 0.0
        
    def add_query_cost(self, model, tokens):
        # Calculate based on current pricing
        pass
```

#### In Provider Dashboards:
- Set monthly spending limits
- Enable usage notifications
- Review spending regularly

### Cost Optimization Tips

1. **Start Small**: Test with 10-20 queries before running 100+
2. **Use Haiku for Generation**: It's cheaper and fast enough
3. **Cache Results**: Avoid re-running identical queries
4. **Batch Requests**: Reduce overhead
5. **Monitor Costs**: Check dashboards after each research session

## Alternative Configurations

### Using Different Models

```env
# Use cheaper models
QUERY_MODEL=claude-haiku-4.5
SYNTHESIS_MODEL=claude-sonnet-4.5  # Or haiku for cost savings

# Or use different providers (future support)
QUERY_PROVIDER=anthropic
SEARCH_PROVIDER=perplexity
SYNTHESIS_PROVIDER=anthropic
```

### Local Development

```env
# Use fewer queries for testing
DEFAULT_NUM_QUERIES=10

# Reduce concurrency
MAX_CONCURRENT_SEARCHES=3

# Shorter timeouts
SEARCH_TIMEOUT=15
```

### Production Configuration

```env
# Optimized for production
DEFAULT_NUM_QUERIES=100
MAX_CONCURRENT_SEARCHES=15
SEARCH_TIMEOUT=30
RETRY_ATTEMPTS=3

# Enable detailed logging
LOG_LEVEL=INFO
LOG_FILE=logs/research.log
```

## Example `.env.example` File

Create this as a template for users:

```env
# Ultra Deep Research - API Configuration Template
# Copy this file to .env and fill in your actual API keys

# Required: Anthropic API Key
# Get yours at: https://console.anthropic.com
ANTHROPIC_API_KEY=your_anthropic_key_here

# Required: Perplexity API Key
# Get yours at: https://www.perplexity.ai
PERPLEXITY_API_KEY=your_perplexity_key_here

# Optional: Model Configuration
QUERY_MODEL=claude-haiku-4.5
SYNTHESIS_MODEL=claude-sonnet-4.5

# Optional: Performance Tuning
MAX_CONCURRENT_SEARCHES=15
SEARCH_TIMEOUT=30
RETRY_ATTEMPTS=3

# Optional: Defaults
DEFAULT_NUM_QUERIES=100
DEFAULT_OUTPUT_FILE=research_report.md

# Optional: Logging
LOG_LEVEL=INFO
```

## Next Steps

After setup:
1. ✅ Verify APIs are working
2. ✅ Run a test research: `udr "test topic" --num-queries 10`
3. ✅ Check the output report
4. ✅ Review cost in provider dashboards
5. ✅ Adjust configuration as needed

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX

For questions or issues, see the main [README.md](README.md) or open a GitHub issue.
