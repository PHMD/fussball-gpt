# KSI Agent Setup - Using Claude Agent SDK

This guide shows how to run the KSI prototype using the Claude Agent SDK, which gives you access to the same agent infrastructure that powers Claude Code.

## Why Use the Agent SDK?

✅ **Your Claude Account** - Use your existing Anthropic API key
✅ **Production Features** - Context management, error handling, session management
✅ **Streaming Responses** - Real-time output as the agent thinks
✅ **Auto-Compaction** - Automatic context window management
✅ **MCP Support** - Extend with custom tools and integrations

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install the Claude Agent SDK
pip install claude-agent-sdk

# Or install all requirements
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
# Option 1: Add to .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env

# Option 2: Export in terminal
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Get your API key from: https://console.anthropic.com/settings/keys

### 3. Run the Agent

```bash
python ksi_agent.py
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User Input                                                 │
│      ↓                                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  KSI Agent (ksi_agent.py)                          │    │
│  │  • Manage conversation state                       │    │
│  │  • Refresh sports data automatically               │    │
│  │  • Inject data context into messages               │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                             │
│               ├─→ Data Aggregator                          │
│               │   • Fetch from Kicker RSS                  │
│               │   • Fetch from TheSportsDB                 │
│               │   • Normalize to common format             │
│               │                                             │
│               └─→ Claude Agent SDK                         │
│                   • Context management                      │
│                   • Streaming responses                     │
│                   • Error handling                          │
│                   • Session tracking                        │
│                   ↓                                         │
│               Anthropic API (your account)                  │
│                   ↓                                         │
│  AI Response (streamed)                                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

**Automatic Data Refresh**
- Sports data is fetched initially and cached
- Auto-refreshes every 5 minutes (configurable)
- Manual refresh with `/refresh` command

**Context Injection**
- Every query includes latest sports data
- Agent has full context of news and schedules
- Answers grounded in real, current data

**Streaming Output**
- Responses stream character-by-character
- See the agent thinking in real-time
- Natural conversation flow

**Built-in Commands**
- `/refresh` - Force data refresh
- `/exit` or `/quit` - Exit cleanly

## Example Session

```
🏆 KSI - Kicker Sports Intelligence
Powered by Claude Agent SDK
======================================================================

Ask me anything about sports!

Commands:
  /refresh - Force data refresh
  /exit or /quit - Exit
======================================================================

[📡 Fetching latest sports data...]
Fetching data from all sources...
Fetched 6 news articles and 10 sports events
[✓ Data refreshed: 6 articles, 10 events]

🏆 You: What happened in the Champions League last night?

🤖 KSI: Based on the latest data, there were two notable Champions League
matches:

1. **PSG 7-2 Bayer Leverkusen** - A dominant performance by Paris St. Germain
at the BayArena. Coach Kasper Hjulmand described it as a "lesson" and pointed
to a crucial 7-minute period after the equalizer where Leverkusen showed
naivety. The match featured 9 goals, 2 penalties, and red cards.

2. **Borussia Dortmund 4-2 FC Copenhagen** - An away victory for Dortmund
with Felix Nmecha scoring twice and new signing Fabio Silva getting his first
goal for the club. Coach Niko Kovac praised the team's second-half
performance.

Would you like more details about either match?

🏆 You: Who scored for Dortmund?

🤖 KSI: For Borussia Dortmund in their 4-2 win at Copenhagen:
- Felix Nmecha scored twice (a brace/Doppelpack)
- Fabio Silva scored his first goal for BVB (premiere)

The team showed strong attacking form with 4 goals, continuing their trend of
high-scoring performances this season.
```

## Configuration Options

### Data Refresh Interval

Modify in `ksi_agent.py`:

```python
ksi = KSISportsAgent(refresh_interval=300)  # seconds
```

### System Prompt

The agent's personality and expertise are defined in the system prompt. Customize in `ksi_agent.py`:

```python
system_prompt = """You are KSI (Kicker Sports Intelligence)...
```

### Permission Mode

Control tool access:

```python
options = AgentOptions(
    permission_mode="allow_all",  # or "deny_all", "prompt"
    allowed_tools=["bash", "read"],  # specific tools
)
```

## Advanced Usage

### Single Query Mode

Use the agent programmatically:

```python
from ksi_agent import KSISportsAgent

ksi = KSISportsAgent()
response = await ksi.query_once("What are the latest Bundesliga results?")
print(response)
```

### Custom MCP Integration

Extend with custom tools by configuring MCP servers in `.claude/config.json`:

```json
{
  "mcpServers": {
    "sports-stats": {
      "command": "node",
      "args": ["path/to/sports-stats-mcp-server.js"]
    }
  }
}
```

### Session Management

The Agent SDK handles session state automatically:
- Context is preserved across queries
- Auto-compaction prevents context overflow
- Session history maintained for coherent conversations

## Comparison: SDK vs Direct API

| Feature | Direct API (cli.py) | Agent SDK (ksi_agent.py) |
|---------|-------------------|-------------------------|
| Context Management | Manual | Automatic |
| Streaming | Manual implementation | Built-in |
| Error Handling | Basic | Production-ready |
| Tool Integration | Limited | Full MCP support |
| Session State | Manual | Automatic |
| Code Complexity | Higher | Lower |
| Extensibility | Limited | High (MCP) |

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set it
export ANTHROPIC_API_KEY=your_key_here
```

**Import errors**
```bash
# Reinstall SDK
pip install --upgrade claude-agent-sdk

# Or use venv
venv/bin/pip install claude-agent-sdk
```

**No data fetched**
- Check internet connection
- RSS feeds may be temporarily unavailable
- Sports API has rate limits (should work with free tier)

**Agent responses are slow**
- This is normal - using Sonnet 3.5 for quality responses
- Data aggregation happens in background
- First query after refresh may be slower

## Next Steps

1. **Customize the system prompt** - Make the agent's personality match your needs
2. **Add MCP tools** - Integrate databases, APIs, custom data sources
3. **Build a web UI** - Wrap the agent in a FastAPI/Flask backend
4. **Add memory** - Implement conversation history storage
5. **Multi-agent** - Create specialized sub-agents for different sports

## Resources

- [Claude Agent SDK Docs](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Anthropic API Console](https://console.anthropic.com/)
- [Agent SDK Python GitHub](https://github.com/anthropics/claude-agent-sdk-python)
