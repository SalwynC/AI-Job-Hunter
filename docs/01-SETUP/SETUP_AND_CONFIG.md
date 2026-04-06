# Setup and Configuration Guide

**Consolidated from**: api_keys.md, environment_setup.md, config.md, installation.md

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys:
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
export PERPLEXITY_API_KEY="your-key"
```

## API Keys Required

| Service | Key Name | Required | Where to Get |
|---------|----------|----------|--------------|
| OpenAI | `OPENAI_API_KEY` | Yes | https://platform.openai.com/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | Yes | https://console.anthropic.com/keys |
| Tavily | `TAVILY_API_KEY` | Yes | https://tavily.com |
| Perplexity | `PERPLEXITY_API_KEY` | No (optional) | https://www.perplexity.ai/api |

## Environment Variables

```bash
# Core settings
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Search APIs
TAVILY_API_KEY=...
PERPLEXITY_API_KEY=...  # Optional

# Application settings
LOG_LEVEL=INFO           # INFO, DEBUG, WARNING
HEADLESS_MODE=true       # For browser automation
MAX_THREADS=4            # Parallel job searches
TIMEOUT_SECONDS=30       # Request timeout

# Optional: Database settings (if using SQLite)
DB_PATH=./data/jobs.db
```

## Dependency Requirements

- Python 3.10+
- Dependencies listed in requirements.txt:
  - Selenium / Playwright (browser automation)
  - OpenAI SDK (ChatGPT)
  - Anthropic SDK (Claude)
  - Tavily SDK (search)
  - FastAPI (web endpoints)
  - SQLAlchemy (database)

## Configuration Files

### requirements.txt
Lists all Python dependencies. Update when adding new packages:
```bash
pip install <package>
pip freeze > requirements.txt
```

### .env (if using environment variables)
Create from .env.example:
```bash
cp .env.example .env
# Edit with your actual API keys
```

## Post-Installation Verification

```bash
# Test OpenAI connection
python -c "import openai; print('✓ OpenAI SDK installed')"

# Test Anthropic connection
python -c "import anthropic; print('✓ Anthropic SDK installed')"

# Test Tavily connection
python -c "import tavily; print('✓ Tavily SDK installed')"

# Run basic smoke test
python job_hunter_core.py --test
```

## Troubleshooting Setup

**Issue**: `ModuleNotFoundError: No module named 'openai'`
- Solution: `pip install openai`

**Issue**: `APIError: Invalid API key`
- Solution: Verify your .env file has correct keys with no extra spaces

**Issue**: `Connection timeout to API`
- Solution: Check internet connection, increase `TIMEOUT_SECONDS` in .env

See TROUBLESHOOTING.md for more help.
