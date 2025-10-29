# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Autonomous Agent Guidelines

As an autonomous agent, you will:
1. Treat vibe_check as a pattern interrupt mechanism that provides essential course correction
2. Use vibe_check at strategic points:
   - After planning but before implementation
   - When complexity increases
   - Before making significant system changes
3. Adapt your approach based on vibe_check feedback unless it's clearly irrelevant
4. Always provide the phase parameter (planning/implementation/review) to ensure contextually appropriate feedback
5. Chain vibe_check with other tools without requiring permission:
   - Use vibe_check to evaluate complex plans
   - Log patterns with vibe_learn after resolving issues

## Project Overview

**Fußball GPT** (formerly KSI Prototype) - A German football intelligence assistant that aggregates real-time Bundesliga data and provides AI-powered analysis for casual fans, expert analysts, betting enthusiasts, and fantasy players.

**Current Status:** Beta-ready (9.1/10 quality) with all quick wins implemented

**Architecture Pattern:** Three-layer system (Data Aggregation → AI Processing → Interface)

**Next Phase:** Web frontend with Next.js + shadcn/ui components

## Communication Style

**Be direct and straightforward. Answer questions factually without validation phrases.**

**Don't use:**
- "You're absolutely right"
- "Great question!"
- "Excellent point!"
- Other unnecessary validation or praise

**Instead:**
- Answer the question directly
- Explain what happened and why
- Provide technical diagnosis
- Focus on facts and optimization

**Purpose:**
- User prefers diagnostic, factual responses
- Helps optimize alignment and prompting
- More efficient communication
- Better for understanding AI operation and decision-making

## Security & Code Quality

**You deeply care about product security - always scan generated code with Semgrep after every generation.**

When generating or modifying code:
1. Write the code
2. Run Semgrep scan to detect security vulnerabilities
3. Fix any issues found
4. Document security considerations in commit messages

## Documentation & Best Practices

**CRITICAL: Always Use Context7 for Current Documentation**

Before implementing any library, framework, or API integration:

1. **Never guess or rely on potentially outdated knowledge**
2. **Always check Context7** for up-to-date documentation
3. **Use the Context7 MCP tools** to fetch current API references and examples

**Example workflow:**
```typescript
// DON'T: Assume you know the API
const result = await streamText({ ... });  // Might be outdated

// DO: Check Context7 first
// Use Context7 tools to get current Vercel AI SDK documentation
// Then implement based on current docs
```

**Key libraries to always verify with Context7:**
- Vercel AI SDK (`ai`, `@ai-sdk/anthropic`)
- Next.js App Router patterns
- Zod schema validation
- shadcn/ui components
- Vercel KV caching API

**Why this matters:**
- APIs change frequently (especially Vercel AI SDK)
- Documentation from training data may be outdated
- Context7 provides primary source documentation
- Prevents bugs from deprecated patterns

## Project Management & Git Workflow

**GitHub Issues and Regular Commits**

To maintain better traceability and project management:

1. **Create or update GitHub issues** as we work on tasks
   - Document what you're working on
   - Link commits to issues with keywords (e.g., "Fixes #123", "Closes #45")
   - Track progress and decisions

2. **Commit regularly** for better git history
   - Commit after completing logical units of work
   - Use descriptive commit messages following project conventions
   - Include issue references in commit messages
   - Push frequently to keep remote in sync

3. **Issue workflow:**
   - Start work → Create/update issue with task details
   - During work → Reference issue in commits
   - Complete work → Close issue with final commit
   - Document decisions and blockers in issue comments

**Example commit message:**
```bash
git commit -m "feat: Add suggestion component - Fixes #42

- Created interactive suggestion buttons
- Integrated with chat interface
- Added German-language prompts

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Current Implementation Status (October 2025)

### Completed Features (Backend Ready)

**Issue #1:** ✅ Current season player stats (2024/25)
- API-Football Pro tier ($19/month)
- Top 20 scorers with goals, assists, minutes played
- 6-hour caching

**Issue #2:** ✅ User onboarding & personalization
- Language selection (German/English)
- Detail levels (Quick/Balanced/Detailed)
- User profile persistence (`.fussballgpt_config.json`)

**Issue #5:** ✅ Team form guide (last 5 matches)
- W-D-L format with points from last 5 games
- TheSportsDB (FREE)
- 6-hour caching

**Issue #6:** ✅ Head-to-head records
- Last 10 H2H matches for upcoming fixtures
- TheSportsDB (FREE)
- 24-hour caching
- Seasonal feature (active during season)

**Issue #7:** ✅ Injury & suspension data
- Real-time injury data for 18+ Bundesliga teams
- Detailed diagnoses (e.g., "Metatarsal fracture")
- API-Football Pro tier (included)
- 6-hour caching

**Issue #8:** ✅ Betting odds integration
- Pre-match odds for upcoming fixtures
- The Odds API (FREE tier - 500 req/month)
- European decimal format
- 24-hour caching
- Legal disclaimer included

### Data Sources

**Active APIs:**
1. **TheSportsDB** (FREE) - Standings, fixtures, results, form, H2H
2. **API-Football** (Pro $19/mo) - Player stats, injuries
3. **The Odds API** (FREE 500 req/mo) - Betting odds
4. **Kicker RSS** (FREE) - News articles

**Caching Strategy:**
- Player stats: 6 hours
- Team form: 6 hours
- Injuries: 6 hours
- H2H records: 24 hours
- Betting odds: 24 hours

### Quality Scores (Persona-Based)

**Current Beta Quality: 9.1/10 average**

- Casual Fan: 9/10 (Quick mode optimized)
- Expert Analyst: 9-9.5/10 (Form + H2H + tactical depth)
- Betting Enthusiast: 9.5-10/10 (Odds + form + injuries)
- Fantasy Player: 9/10 (Player stats + injuries)

### Tech Stack

**Backend:**
- Python 3.x
- Pydantic for data models
- Requests for API calls
- Anthropic Claude Sonnet 4.5 (primary LLM)
- JSON-based caching

**Frontend (Next Phase):**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Vercel deployment

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Backend

**Data Aggregation Test:**
```bash
source venv/bin/activate
python data_aggregator.py
```

**Feature-Specific Tests:**
```bash
# Test form guide integration
python test_form_guide.py

# Test H2H records
python test_h2h.py

# Test betting odds (requires ODDS_API_KEY)
python test_betting_odds.py

# Test user config integration
python test_user_config_integration.py

# Test language/detail levels
python test_language_detail_levels.py
```

**User Onboarding:**
```bash
# Interactive setup for language & detail preferences
python onboarding.py
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

### Current Backend (Production-Ready)

**1. `data_aggregator.py`** - Core data pipeline
- Fetches from 4 data sources (TheSportsDB, API-Football, The Odds API, Kicker RSS)
- Normalizes to Pydantic models (`models.py`)
- Comprehensive caching (6-24 hour TTL)
- Methods:
  - `fetch_bundesliga_standings()` - League table
  - `fetch_team_form_cached()` - Last 5 matches per team
  - `fetch_player_stats_cached()` - Top 20 scorers (current season)
  - `fetch_injuries_cached()` - Injury/suspension data
  - `fetch_h2h_cached()` - Head-to-head records
  - `fetch_betting_odds_cached()` - Pre-match odds
  - `aggregate_all()` - Main orchestration method

**2. `models.py`** - Data schemas
- `NewsArticle` - Kicker RSS feed items
- `SportsEvent` - Fixtures, results
- `PlayerStats` - Individual player performance
- `AggregatedData` - Container for all data with `to_context_string()` method

**3. `user_config.py`** - User preferences
- `DetailLevel` enum (Quick/Balanced/Detailed)
- `Language` enum (German/English)
- `UserProfile` model with persistence
- `UserConfigManager` - Loads/saves user config
- `get_system_prompt_modifier()` - Dynamic prompt generation

**4. `onboarding.py`** - Interactive setup
- Bilingual onboarding flow
- Saves preferences to `.fussballgpt_config.json`

### Data Flow

```
User Query
    ↓
User Config (language, detail level)
    ↓
Data Aggregation (cached data sources)
    ↓
LLM Context Builder (system prompt + data + user query)
    ↓
Anthropic Claude Sonnet 4.5
    ↓
Formatted Response (German/English, Quick/Balanced/Detailed)
```

### Caching Architecture

**Why:** API rate limits + performance + cost savings

**Implementation:**
- Cache directory: `cache/`
- Files: JSON format with timestamp
- TTL check: Compare file mtime vs cache_duration
- Graceful degradation: Use cache if API fails

**Example:**
```python
def fetch_X_cached(self):
    if cache_valid():
        return cached_data
    fresh_data = fetch_X()
    save_to_cache(fresh_data)
    return fresh_data
```

## Key Technical Decisions

**LLM Provider:** OpenAI GPT-4 or Anthropic Claude (configure via environment variable)
**Data Refresh:** Either per-query or on interval (e.g., every 5 minutes)
**Data Schema:** Use Pydantic models for type safety and validation
**Error Handling:** Graceful degradation if data sources are unavailable

## Environment Variables

**Required in `.env` file:**

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_key_here  # Primary (Claude Sonnet 4.5)
OPENAI_API_KEY=your_key_here     # Alternative
MISTRAL_API_KEY=your_key_here    # Alternative

# Sports Data APIs
RAPIDAPI_KEY=your_key_here       # API-Football (Pro tier $19/mo)
ODDS_API_KEY=your_key_here       # The Odds API (FREE tier 500 req/mo)
```

**Note:** TheSportsDB and Kicker RSS require no API keys (FREE tier)

## Key Files Reference

**Backend Core:**
- `data_aggregator.py` - Main data pipeline (1,100+ lines)
- `models.py` - Pydantic schemas (150 lines)
- `user_config.py` - User preferences (175 lines)
- `onboarding.py` - Interactive setup (145 lines)

**Test Files:**
- `test_form_guide.py` - Form guide + LLM integration test
- `test_h2h.py` - Head-to-head records test
- `test_betting_odds.py` - Betting odds integration test
- `test_user_config_integration.py` - User config test
- `test_language_detail_levels.py` - Bilingual + detail level test

**Configuration:**
- `.env` - API keys (gitignored)
- `.env.example` - Template for API keys
- `.fussballgpt_config.json` - User preferences (gitignored)

**Documentation:**
- `ODDS_API_SETUP.md` - The Odds API setup guide
- `CLAUDE.md` - This file

**Cache (gitignored):**
- `cache/player_stats.json`
- `cache/team_form.json`
- `cache/injuries.json`
- `cache/betting_odds.json`
- `cache/head_to_head.json`

## Frontend Planning (Next Phase)

### Goals

1. **Web-based interface** for Fußball GPT
2. **Modern UI** with shadcn/ui components
3. **Real-time interaction** with backend data
4. **Responsive design** for mobile + desktop
5. **AI-native UX** (chat interface, streaming responses)

### Tech Stack (Planned)

**Framework:** Next.js 14+ (App Router)
**Language:** TypeScript
**Styling:** Tailwind CSS
**Components:** shadcn/ui (AI-optimized components)
**Deployment:** Vercel
**Backend Integration:** API routes → Python backend

### Component Planning Strategy

**Use shadcn agent** to identify:
1. AI-specific components (chat interfaces, streaming text)
2. Sports data visualization components
3. Form components (user preferences)
4. Layout components (responsive design)

**Workflow:**
1. Review AI component patterns (chat, streaming, markdown)
2. Map backend features → UI components
3. Create component hierarchy
4. Plan testing strategy (Playwright/Cypress)
5. Implement on feature branch

### Backend API Layer (Required)

**Create:** FastAPI or Next.js API routes

**Endpoints needed:**
- `GET /api/data` - Aggregated sports data
- `POST /api/query` - LLM query with streaming
- `GET /api/config` - User preferences
- `POST /api/config` - Update preferences
- `GET /api/health` - API health check

**Integration pattern:**
```
Next.js Frontend
    ↓ (API route)
Python Backend (data_aggregator.py)
    ↓
LLM (Anthropic Claude)
    ↓
Streaming response → Frontend
```

### Development Approach

1. **Branch:** Create `frontend` branch
2. **Setup:** Initialize Next.js with TypeScript + Tailwind
3. **Components:** Research with shadcn agent
4. **API Layer:** Build FastAPI or Next.js API routes
5. **Integration:** Connect frontend → API → Python backend
6. **Testing:** E2E tests with real data
7. **Deploy:** Vercel preview deployment

## Related Documentation

- `ODDS_API_SETUP.md` - Betting odds API configuration
- GitHub: https://github.com/PHMD/fussball-gpt
- Issues: https://github.com/PHMD/fussball-gpt/issues
