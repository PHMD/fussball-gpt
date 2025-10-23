# ⚽ Fußball GPT

**AI für deutschen Fußball**

An AI-powered assistant for German football fans, providing real-time Bundesliga stats, tactical analysis, and news in professional German journalism style.

## 🎯 Features

- **Real-time Bundesliga standings** from TheSportsDB (free tier)
- **Latest news** from Kicker.de RSS feeds
- **Player statistics** from API-Football (goals, assists, cards, minutes)
- **Multi-turn conversations** with context retention (8.0/10 tested)
- **Professional German journalism tone** (8.5/10 quality)
- **Error handling** (91.7% pass rate on edge cases)

## 🚀 Setup

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

## ⚖️ Legal & Compliance

**Product Name:** "Fußball GPT"
- ✅ No trademark conflicts with DFL
- Safe from legal issues

**Required Disclaimer:**
```
This product is not affiliated with, sponsored by, or endorsed by
Deutsche Fußball Liga GmbH or the Bundesliga. All trademarks are
property of their respective owners.
```

**Data Attribution:**
- Powered by Kicker.de news
- Real-time data from TheSportsDB & API-Football

## 📊 Beta Test Results

**Ready for beta launch:** ✅

- **Multi-Turn Conversations:** 8.0/10 (context retention works well)
- **Error Handling:** 91.7% pass rate (graceful degradation)
- **Multi-Persona Testing:**
  - Expert Analyst: 8-9/10 ✅
  - Betting Enthusiast: 6-9/10 ✅
  - Casual Fan: 5/10 ⚠️
  - Fantasy Player: 2-8/10 ⚠️

See `BETA_LAUNCH_READY.md` for complete test results.

## 📄 License

MIT License

---

**Fußball GPT** - AI für deutschen Fußball
