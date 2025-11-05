# KSI Quick Start - 5 Minutes to Running

Get the sports intelligence agent running in 5 minutes using your Claude account.

## Prerequisites

- Python 3.8+ installed
- Anthropic API key ([Get one here](https://console.anthropic.com/settings/keys))

## Steps

### 1. Clone/Navigate to Project
```bash
cd /path/to/ksi_prototype
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your key
# ANTHROPIC_API_KEY=sk-ant-...
```

Or just export it:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 4. Run the Agent
```bash
python ksi_agent.py
```

## First Conversation

```
🏆 You: What happened in the Champions League last night?

🤖 KSI: [Streams response about latest matches from real data]

🏆 You: Who scored for Dortmund?

🤖 KSI: [Provides scorer details from aggregated data]
```

## Commands

- `/refresh` - Force data refresh
- `/exit` - Exit the agent

## What You Get

✅ **Real sports data** from Kicker.de and TheSportsDB
✅ **Streaming responses** as the agent thinks
✅ **Automatic context management** (no token limit worries)
✅ **Natural language** understanding powered by Claude
✅ **Production-ready** error handling and session management

## Next Steps

- **Customize the prompt**: Edit `system_prompt` in `ksi_agent.py`
- **Add more data sources**: Extend `data_aggregator.py`
- **Build a web UI**: Wrap the agent in FastAPI/Flask
- **Add MCP tools**: Integrate custom data sources

See [AGENT_SETUP.md](AGENT_SETUP.md) for advanced configuration.

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you created the `.env` file
- Or export the key in your terminal

**"No module named 'claude_agent_sdk'"**
```bash
pip install claude-agent-sdk
```

**No data appears**
- Check your internet connection
- RSS feeds should work without auth
- Sports API uses free tier by default

## Cost Estimate

Using the Claude Agent SDK with your API key:

- **Sonnet 3.5**: ~$0.003 per message (input) + ~$0.015 per response
- **Typical query**: $0.02 - $0.05
- **100 queries**: ~$2 - $5

Data aggregation is free (public APIs).
