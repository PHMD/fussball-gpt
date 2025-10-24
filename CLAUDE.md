# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Fußball GPT** (formerly KSI Prototype) - An AI-powered Bundesliga assistant that aggregates real-time sports data and provides intelligent analysis through natural language queries.

**Current Status:** Beta-ready (9.1/10 quality)
**Architecture:** Three-layer system (Data Aggregation → AI Processing → Interface)
**Target Users:** Casual fans, expert analysts, betting enthusiasts, fantasy players

---

## Quick Start

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run onboarding (sets language + detail preferences)
python onboarding.py
```

### Running the CLI

**Production (Recommended):**
```bash
python ksi_agent.py
```

**Required:** `ANTHROPIC_API_KEY` in `.env`

### Testing Individual Features
```bash
python data_aggregator.py          # Test all data sources
python test_form_guide.py          # Test form guide + LLM
python test_betting_odds.py        # Test odds API (requires ODDS_API_KEY)
python test_h2h.py                 # Test head-to-head records
```

---

## Current State (October 2025)

### ✅ Completed Features

**Phase 1: Core Backend (Complete)**
- ✅ Issue #1: Current season player statistics (API-Football Pro tier)
- ✅ Issue #2: User onboarding (language: DE/EN, detail levels: Quick/Balanced/Detailed)
- ✅ Issue #5: Team form guide (last 5 matches, W-D-L format)
- ✅ Issue #6: Head-to-head records (last 10 matches between teams)
- ✅ Issue #7: Injury & suspension data (18+ Bundesliga teams)
- ✅ Issue #8: Betting odds integration (The Odds API)

**Phase 2: Quality & Optimization (Complete)**
- ✅ Bilingual support (German/English) via system prompts
- ✅ User preference management (stored in `.fussballgpt_config.json`)
- ✅ Comprehensive caching (6h for stats/form/injuries, 24h for odds/H2H)
- ✅ Persona testing (Casual Fan, Expert Analyst, Betting Enthusiast, Fantasy Player)

### 🚧 Next Phase: Frontend (Starting)

**Phase 3: Web Interface**
- Web UI with Next.js (TypeScript + Tailwind + shadcn/ui)
- Responsive design for mobile/desktop
- Real-time query interface
- User preference management UI
- Match cards with odds, form, injuries
- Component planning with shadcn agent

---

## Data Sources & APIs

### Active Integrations

**1. TheSportsDB (FREE)**
- Standings, fixtures, results
- Team form (last 5 matches)
- Head-to-head records
- Rate limit: 30 req/min
- Cache: 6 hours (form), 24 hours (H2H)

**2. API-Football (Pro tier $19/month)**
- Current season player statistics (2024/25 Bundesliga)
- Injury & suspension data
- Rate limit: Generous on Pro tier
- Cache: 6 hours

**3. The Odds API (FREE tier 500 req/month)**
- Pre-match betting odds (decimal format)
- European bookmakers
- Rate limit: 500 req/month
- Cache: 24 hours

**4. Kicker RSS (FREE)**
- German football news
- Latest articles and updates
- No rate limit

---

## Architecture

### Backend Structure

**Core Files:**
```
data_aggregator.py      # Data ingestion from all APIs
models.py              # Pydantic models (NewsArticle, SportsEvent, PlayerStats)
user_config.py         # User preference management
onboarding.py          # Interactive setup flow
ksi_agent.py          # Main CLI with Claude Agent SDK
```

**Configuration:**
```
.env                   # API keys (gitignored)
.fussballgpt_config.json  # User preferences (gitignored)
```

**Caching:**
```
cache/
├── player_stats.json      # 6-hour TTL
├── team_form.json         # 6-hour TTL
├── injuries.json          # 6-hour TTL
├── betting_odds.json      # 24-hour TTL
└── head_to_head.json      # 24-hour TTL
```

### Data Flow

```
User Query (German/English, Quick/Balanced/Detailed)
    ↓
data_aggregator.aggregate_all()
    ↓
Check cache (TTL-based)
    ↓
Fetch from APIs (if cache expired)
    ├─ TheSportsDB: standings, form, H2H
    ├─ API-Football: player stats, injuries
    ├─ The Odds API: betting odds
    └─ Kicker RSS: news
    ↓
Normalize to Pydantic models
    ↓
Build LLM context (standings + form + injuries + H2H + odds + news)
    ↓
Apply user preferences (language + detail level)
    ↓
Send to Claude with system prompt
    ↓
Stream response to user
```

### Caching Strategy

**Why caching is critical:**
1. **API rate limits:** Free tier APIs have strict limits (30-500 req/day or month)
2. **Cost management:** Paid API (API-Football) costs $19/month - cache reduces calls by 95%
3. **Performance:** Sub-second responses from cache vs 5-10 seconds from APIs
4. **Graceful degradation:** System works even when APIs hit rate limits

**Cache durations:**
- **6 hours:** Data that changes with matches (stats, form, injuries)
- **24 hours:** Data that's stable (odds, H2H history)

---

## User Preferences

### Language Support
- **German (default):** Native language for Bundesliga content
- **English:** International audience

**Implementation:** System prompt changes, not model retraining

### Detail Levels

**Quick (1-2 sentences):**
- Casual fans who want headlines
- Example: "Bayern führt mit 82 Punkten, 13 vor Leverkusen."

**Balanced (2-3 paragraphs):** [DEFAULT]
- Standard journalistic style
- Facts + context + occasional tactical insights

**Detailed (3-5+ paragraphs):**
- Expert analysts
- Tactical depth, statistical evidence, comparisons

---

## Environment Variables

```bash
# LLM API (required)
ANTHROPIC_API_KEY=your_key_here

# Sports Data APIs
RAPIDAPI_KEY=your_key_here           # API-Football (Pro tier $19/mo)
ODDS_API_KEY=your_key_here           # The Odds API (FREE, 500 req/mo) - OPTIONAL

# Alternative LLM providers (optional)
OPENAI_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

**Setup The Odds API (optional but recommended for betting features):**
1. Get free API key at https://the-odds-api.com/
2. Add to `.env` as `ODDS_API_KEY=your_key`
3. See `ODDS_API_SETUP.md` for details

---

## Persona Quality Scores

**Current beta quality: 9.1/10 average**

| Persona | Score | Key Features |
|---------|-------|--------------|
| Casual Fan | 9/10 | Quick mode, simple language |
| Expert Analyst | 9-9.5/10 | Detailed mode, tactical depth, form + H2H |
| Betting Enthusiast | 9.5-10/10 | Odds + form + injuries + H2H 🎯 |
| Fantasy Player | 9/10 | Player stats + injuries |

**How we got here:**
- Issue #1 (Player Stats): +1.0 for Fantasy
- Issue #2 (Onboarding): +0.5 across all personas
- Issue #5 (Form Guide): +1.0 Betting, +0.5 Analyst
- Issue #6 (H2H Records): +0.5 Betting, +0.5 Analyst
- Issue #7 (Injuries): +0.5-1.0 Betting, +0.5 Fantasy
- Issue #8 (Odds API): +1.5 Betting 🎯

---

## Development Workflow

### Phase 3: Frontend Development (Next)

**Tech Stack (per user preferences):**
- **Framework:** Next.js 14+ (React, TypeScript)
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui (copy/paste, customizable)
- **Deployment:** Vercel (git push to deploy)

**Component Planning:**
1. Use shadcn agent to identify best components
2. Review AI-specific components (chat interfaces, streaming)
3. Plan testing strategy
4. Create feature branch: `frontend-phase-3`

**Key Features to Build:**
- Chat-style interface for queries
- Match cards showing odds, form, injuries
- User preference toggle (language, detail level)
- Responsive mobile/desktop design

### Git Workflow

**Main branch:** `master` (protected, beta-ready backend)
**Feature branches:** `frontend-phase-3`, `feature/xyz`
**Commits:** Use conventional commits with co-author attribution

```bash
# Create feature branch
git checkout -b frontend-phase-3

# Commit format
git commit -m "feat: add match card component

- Display odds, form, injuries
- Responsive design
- shadcn/ui Card component

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Testing Strategy

### Backend Tests (Complete)
```bash
pytest                              # All tests
python test_form_guide.py           # Form guide + LLM integration
python test_betting_odds.py         # Odds API
python test_h2h.py                  # Head-to-head records
python test_language_detail_levels.py  # Bilingual + detail levels
```

### Frontend Tests (Upcoming)
- Component testing (Jest + React Testing Library)
- E2E testing (Playwright)
- Visual regression (Chromatic/Percy)
- API mocking (MSW)

---

## API Quota Management

**Monthly Usage (with caching):**
- TheSportsDB: ~500 requests (well under 30/min limit)
- API-Football: ~240 requests (Pro tier: generous)
- The Odds API: ~30 requests (well under 500/month limit)

**Without caching, we'd use:**
- 4,500+ API-Football requests/month (expensive overages)
- 500 Odds API requests in 1 day (immediate limit)

**Caching saves ~95% of API costs**

---

## Known Issues & Limitations

### Seasonal Features
- **H2H records:** Only available during Bundesliga season with scheduled fixtures
- **Off-season:** Gracefully handles missing data (no fixtures = no H2H displayed)

### Rate Limiting
- **TheSportsDB:** May hit 30 req/min during heavy testing
- **Mitigation:** Caching handles gracefully, uses cached data when limits hit

### API-Football Free Tier
- **Season access:** Free tier limited to historical seasons (2021-2023)
- **Current project:** Uses Pro tier ($19/mo) for current season (2024/25)

---

## Documentation

**Setup & Configuration:**
- `README.md` - Project overview
- `QUICK_START.md` - Getting started guide
- `ODDS_API_SETUP.md` - Betting odds API setup

**Development:**
- `KSI_PROTOTYPE_DEVELOPMENT_BRIEF.md` - Original specification
- Knowledge base: `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype/`

**Related Knowledge Base Files:**
- `[[ksi_prototype_specification]]`
- `[[kicker_ai_platform_architecture]]`

---

## Contact & Support

**GitHub:** https://github.com/PHMD/fussball-gpt
**Issues:** https://github.com/PHMD/fussball-gpt/issues

---

## Next Steps (Post-Compact)

**Phase 3: Frontend Development**

1. **Component Planning (with shadcn agent):**
   - Identify required shadcn components
   - Review AI-specific components (chat, streaming)
   - Plan responsive layout

2. **Architecture Design:**
   - Next.js app structure
   - API routes for backend integration
   - State management strategy

3. **Testing Strategy:**
   - Component tests
   - E2E tests
   - API mocking

4. **Git Workflow:**
   - Create `frontend-phase-3` branch
   - Plan feature increments
   - Define merge strategy

**Goal:** Production-ready web interface for Fußball GPT beta launch
