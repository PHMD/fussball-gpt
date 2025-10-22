# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kicker Sports Intelligence (KSI) Prototype** - A CLI-based proof-of-concept that aggregates real-time sports data and news from public sources, then uses LLM-powered RAG to answer natural language queries about sports.

**Architecture Pattern:** Three-layer system (Data Aggregation → AI Processing → Interface)

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Prototype

**Production (Recommended): Claude Agent SDK**
```bash
# Run with full agent capabilities
python ksi_agent.py

# Requires ANTHROPIC_API_KEY in .env
```

**Development: Direct API**
```bash
# Basic CLI with direct API calls
python cli.py

# Requires OPENAI_API_KEY or ANTHROPIC_API_KEY in .env
```

**Testing: Data Only**
```bash
# Test data aggregation without LLM
python data_aggregator.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_aggregator.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Core Architecture

### Two-Script Foundation

**1. `data_aggregator.py`** - Data ingestion layer
- Fetches from multiple public sources (Kicker API, RSS feeds, sports APIs)
- Normalizes all data into consistent format (Pydantic models recommended)
- Each data item must include: `source`, `title`, `content`, `timestamp`
- Designed to be imported by CLI or run standalone

**2. `cli.py`** - RAG-powered interface
- Simple `while True` loop accepting user queries
- Imports `data_aggregator.py` to fetch fresh data
- Constructs LLM prompts with user query + aggregated data context
- Sends to LLM API (OpenAI GPT-4 or Anthropic Claude)
- Displays AI response to console

### Data Sources Integration

**Kicker News:** Use `kickerde-api-client` Python package
**Kicker RSS:** Parse feeds from `https://newsfeed.kicker.de/opml`
**Sports Data:** Public API (TheSportsDB or equivalent) for scores/schedules/stats

All sources normalized to consistent schema before LLM processing.

### RAG Pattern Implementation

1. User enters natural language query (CLI)
2. Fetch latest aggregated sports data
3. Build prompt: `[System Context: {aggregated_data}] [User Query: {query}]`
4. Send to LLM API
5. Stream/return response to console

## Key Technical Decisions

**LLM Provider:** OpenAI GPT-4 or Anthropic Claude (configure via environment variable)
**Data Refresh:** Either per-query or on interval (e.g., every 5 minutes)
**Data Schema:** Use Pydantic models for type safety and validation
**Error Handling:** Graceful degradation if data sources are unavailable

## Environment Variables

```bash
# Required for LLM integration
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here

# Optional: configure data refresh interval
DATA_REFRESH_INTERVAL=300  # seconds
```

## Future Phases (Not in Scope Yet)

**Phase 3:** Web API layer (Flask/FastAPI) to expose backend for web frontend. Do not implement until CLI prototype is validated.

## Development Workflow

1. **Start with data aggregation:** Get `data_aggregator.py` working with at least one source
2. **Add sources incrementally:** Kicker API → RSS → Sports API
3. **Build CLI shell:** Simple loop that accepts input
4. **Integrate LLM:** Connect aggregated data + user query → LLM → response
5. **Test end-to-end:** Verify complete flow works before expanding

## Related Documentation

- `KSI_PROTOTYPE_DEVELOPMENT_BRIEF.md` - Full development specification
- Knowledge base references: `[[ksi_prototype_specification]]`, `[[kicker_ai_platform_architecture]]`
