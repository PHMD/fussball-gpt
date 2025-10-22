# KSI Prototype - Quick Start Guide

A CLI prototype that aggregates real-time sports data and uses LLM-powered RAG to answer natural language queries.

## Setup

1. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API key (OpenAI or Anthropic)
```

## Running the Prototype

### 🚀 Recommended: Claude Agent SDK (Production-Ready)
```bash
python ksi_agent.py
```

**Features:**
- ✅ Streaming responses with real-time output
- ✅ Automatic context management
- ✅ Production error handling
- ✅ Session state management
- ✅ MCP extensibility

See [AGENT_SETUP.md](AGENT_SETUP.md) for detailed setup guide.

### Alternative: Direct API Access
```bash
python cli.py
```

Basic CLI using direct OpenAI/Anthropic API calls.

### Test Data Aggregation Only
```bash
python data_aggregator.py
```

This shows what data is being fetched without querying the LLM.

## Example Queries

- "What are the latest Bundesliga news?"
- "When is the next Bayern Munich match?"
- "Summarize today's sports headlines"
- "What matches are coming up this weekend?"

## Architecture

```
┌─────────────────┐
│  cli.py         │  Interactive loop + RAG prompt construction
└────────┬────────┘
         │
         ├─→ data_aggregator.py  (Fetch & normalize data)
         │   ├─→ Kicker API
         │   ├─→ Kicker RSS
         │   └─→ TheSportsDB API
         │
         └─→ LLM API (OpenAI or Anthropic)
```

## Project Structure

- `cli.py` - Main CLI interface with LLM integration
- `data_aggregator.py` - Data fetching and normalization
- `models.py` - Pydantic schemas for data validation
- `requirements.txt` - Python dependencies
- `.env` - API keys and configuration (create from .env.example)

## Troubleshooting

**"API key not found"**
- Make sure you created `.env` from `.env.example`
- Add your API key for either OpenAI or Anthropic
- Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic`

**"Package not installed"**
- Run `pip install -r requirements.txt` in activated venv
- Check that venv is activated: `which python` should show venv path

**"No data fetched"**
- Some sources may require API keys (check TheSportsDB limits)
- RSS feeds should work without authentication
- Check network connection
