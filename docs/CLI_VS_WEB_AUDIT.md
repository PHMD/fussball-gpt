# CLI vs Web Frontend Feature Audit

**Date:** 2025-10-30
**Purpose:** Comprehensive comparison to align Web Frontend with CLI functionality
**Status:** 🔴 Web Frontend at ~25% feature parity

## Executive Summary

The CLI version (626 lines) has significantly more functionality than the Web Frontend. The Python data aggregator (1,384 lines) integrates 4 data sources with 17 fetch methods, while the web version only uses 1 data source with 1 fetch method.

**Critical Gaps:**
1. ❌ **Missing 3 of 4 API integrations** (API-Football, TheSportsDB, The Odds API)
2. ❌ **No source attribution displayed** (InlineCitation component installed but not integrated)
3. ❌ **No article URL linking** (URLs available but not shown to users)
4. ❌ **No follow-up suggestions** (required in CLI, missing in web)

---

## Data Source Comparison

### CLI (Python - 4 Data Sources)

| Data Source | Methods | Purpose | Status in Web |
|-------------|---------|---------|---------------|
| **Kicker RSS** | `fetch_kicker_rss()` | Bundesliga news articles | ✅ **PORTED** |
| **Kicker API** | `fetch_kicker_api()` | Alternative news source | ❌ Missing |
| **Kicker Brave Search** | `fetch_kicker_articles_brave()` | Fallback article search | ❌ Missing |
| **API-Football** | `fetch_player_stats()`, `fetch_injuries()` | Player stats, injuries | ❌ Missing |
| **TheSportsDB** | `fetch_bundesliga_standings()`, `fetch_recent_results()`, `fetch_team_form()`, `fetch_head_to_head()`, `fetch_h2h_for_upcoming_fixtures()` | Standings, results, team form, H2H | ❌ Missing |
| **The Odds API** | `fetch_betting_odds()` | Betting odds | ❌ Missing |

### Web Frontend (TypeScript - 1 Data Source)

| Data Source | File | Purpose | Status |
|-------------|------|---------|--------|
| **Kicker RSS** | `lib/api-clients/kicker-rss.ts` | Bundesliga news | ✅ Working |
| **API-Football** | - | Player stats, injuries | ❌ Not ported |
| **TheSportsDB** | - | Standings, results, form | ❌ Not ported |
| **The Odds API** | - | Betting odds | ❌ Not ported |

**Gap Analysis:**
- ✅ 1 of 4 data sources ported (25%)
- ❌ 3 of 4 data sources missing (75%)
- ❌ 16 of 17 fetch methods missing

---

## Feature Comparison

### 1. Source Attribution & Citations

#### CLI Implementation ✅
**File:** `cli.py` lines 78-118

**Requirements:**
- EVERY factual statement MUST include source citation
- Applies to both direct facts AND synthesized analysis
- Source mapping documented:
  - Player stats = "via API-Football"
  - Standings = "via TheSportsDB"
  - News = "via Kicker RSS"
  - Betting odds = "via The Odds API"

**Examples provided:**
```
Direct: "Kane has 12 goals this season (via API-Football)."
Grouped: "Kane's 2024/25 season (via API-Football): 12 goals, 3 assists..."
Synthesis: "Bayern has won all 5 matches (via TheSportsDB) with Kane scoring 12 goals (via API-Football)."
```

#### Web Frontend Implementation ❌
**File:** `lib/prompts.ts` lines 120-217

**Status:**
- ✅ System prompt has same citation requirements
- ❌ UI doesn't display citations
- ❌ InlineCitation component installed but not integrated
- ❌ No parsing of citation markers from LLM responses

**Components available:**
- `InlineCitation` - Main wrapper
- `InlineCitationText` - Highlighted text
- `InlineCitationCard` - Hover card container
- `InlineCitationCardTrigger` - Badge showing source (e.g., "kicker.de +2")
- `InlineCitationSource` - Source details (title, URL, description)
- `InlineCitationCarousel` - For multiple sources

**Implementation needed:**
1. Parse LLM responses for citation markers (e.g., `(via API-Football)`)
2. Convert to InlineCitation components in Response renderer
3. Display hover cards with source URLs

---

### 2. Article URL Linking

#### CLI Implementation ✅
**File:** `cli.py` lines 113-116

**Format:**
```
📰 Related from Kicker:
   • [Article Title] → [URL]
   • [Article Title] → [URL]
```

**Requirements:**
- List 2-3 most relevant Kicker articles after answering
- ONLY use URLs from NEWS ARTICLES section
- NEVER invent or use placeholder URLs
- Relevance-first strategy (quality over quantity)
- OK to show zero if nothing relevant

#### Web Frontend Implementation ❌

**Status:**
- ❌ Article URLs not displayed in UI
- ✅ URLs available in `NewsArticle` model (`url` field)
- ❌ No component to render article links

**Implementation needed:**
1. After AI response, show related Kicker articles
2. Render as clickable links using InlineCitation or custom component
3. Filter for relevance (don't show unrelated articles)

---

### 3. Follow-up Suggestions

#### CLI Implementation ✅
**File:** `cli.py` lines 139-165

**Requirements:**
- EVERY response MUST end with follow-up question
- Context-aware based on query type:
  - **Player query** → Team info, upcoming matches, comparisons
  - **Team query** → Player stats, recent form, fixtures
  - **Match query** → H2H records, team form, predictions
  - **Standings query** → Top performers, upcoming fixtures
  - **News query** → Specific topics, personalized feed
- Offer 2-3 specific options (not generic "anything else?")
- Natural and conversational

**Example:**
```
💬 Want to explore more? I can show you:
   • Bayern's next match and team form
   • How Kane compares to other top Bundesliga scorers
```

#### Web Frontend Implementation ❌

**Status:**
- ❌ No follow-up suggestions displayed
- ❌ Not in system prompt
- ❌ No UI component for suggestions (though `Suggestion` component exists for welcome screen)

**Implementation needed:**
1. Add follow-up requirement to system prompt
2. Parse follow-up suggestions from LLM responses
3. Render as clickable `Suggestion` buttons below each response
4. Handle click to submit as new query

---

### 4. Data Availability

#### CLI Data Context ✅
**File:** `data_aggregator.py` (1,384 lines)

**Complete data context includes:**
```python
{
    "news_articles": [...],        # Kicker RSS + API + Brave
    "sports_events": [...],        # TheSportsDB standings + results
    "player_stats": [...],         # API-Football stats
    "team_form": {...},            # TheSportsDB W-D-L records
    "betting_odds": {...},         # The Odds API data
    "injuries": {...},             # API-Football injury data
    "head_to_head": {...},         # TheSportsDB H2H records
}
```

**17 fetch methods with caching:**
1. `fetch_kicker_rss()` - RSS feeds (✅ ported)
2. `fetch_kicker_api()` - API endpoint
3. `fetch_kicker_articles_brave()` - Brave Search fallback
4. `fetch_bundesliga_standings()` - League table
5. `fetch_recent_results()` - Match results
6. `fetch_player_stats()` - Player performance
7. `fetch_player_stats_cached()` - Cached stats
8. `fetch_team_form()` - W-D-L records
9. `fetch_team_form_cached()` - Cached form
10. `fetch_betting_odds()` - Odds data
11. `fetch_betting_odds_cached()` - Cached odds
12. `fetch_head_to_head()` - H2H records
13. `fetch_h2h_for_upcoming_fixtures()` - H2H for next matches
14. `fetch_h2h_cached()` - Cached H2H
15. `fetch_injuries()` - Injury reports
16. `fetch_injuries_cached()` - Cached injuries
17. `fetch_sports_api()` - Sports events

#### Web Frontend Data Context ❌
**File:** `app/api/query/route.ts` lines 55-59

**Current implementation:**
```typescript
const dataContext = toContextString({
  news_articles: newsArticles,  // ✅ Only Kicker RSS working
  sports_events: [],             // ❌ Empty!
  player_stats: [],              // ❌ Empty!
  aggregation_timestamp: new Date(),
});
```

**Gap:**
- Only 1 of 7 data types populated
- Missing: standings, results, team form, betting odds, injuries, H2H

---

### 5. Caching Strategy

#### CLI Implementation ✅
**Caching layers:**
- Session-level cache (5-minute TTL for Brave Search)
- Method-level cache (separate `*_cached()` methods)
- Cache invalidation strategies

#### Web Frontend Implementation ⚠️ Partial
**File:** `lib/cache.ts`

**Status:**
- ✅ Has caching infrastructure (`fetchWithCache`, `CACHE_DURATIONS`)
- ✅ Kicker RSS uses 6-hour cache
- ❌ No cached methods for missing APIs

---

### 6. LLM Configuration

#### CLI Implementation ✅
**Model:** Claude Sonnet 4.5 (`claude-sonnet-4.5-20250929`)
**Temperature:** 0.7 (configurable)
**Max tokens:** 2048

#### Web Frontend Implementation ✅
**Model:** Claude Sonnet 4.5 (`claude-sonnet-4-20241022`)
**Temperature:** 0.7
**Max tokens:** 2048
**Streaming:** ✅ Enabled via Vercel AI SDK

**Note:** Both use Claude Sonnet 4, but different version dates

---

## API Integration Status

### API-Football (❌ Not Ported)
**CLI Methods:**
- `fetch_player_stats(league_id=78, season="2025")`
- `fetch_injuries(league_id=78, season="2025")`
- Cached versions of both

**Data provided:**
- Player goals, assists, minutes played, appearances
- Injury status, estimated return dates
- Team-level stats aggregation

**Required for Web:**
1. Create `lib/api-clients/api-football.ts`
2. Port player stats endpoint
3. Port injuries endpoint
4. Add to API route data fetching

---

### TheSportsDB (❌ Not Ported)
**CLI Methods:**
- `fetch_bundesliga_standings()`
- `fetch_recent_results()`
- `fetch_team_form()`
- `fetch_head_to_head(team_id1, team_id2)`
- `fetch_h2h_for_upcoming_fixtures()`
- Cached versions

**Data provided:**
- League standings (position, points, goal difference)
- Match results (scores, dates)
- Team form (W-D-L records for last 5 matches)
- Head-to-head records between teams

**Required for Web:**
1. Create `lib/api-clients/thesportsdb.ts`
2. Port all 5 methods
3. Add caching layer
4. Add to API route data fetching

---

### The Odds API (❌ Not Ported)
**CLI Methods:**
- `fetch_betting_odds()`
- `fetch_betting_odds_cached()`

**Data provided:**
- Betting odds for upcoming matches
- Multiple bookmakers
- Win/Draw/Lose odds

**Required for Web:**
1. Create `lib/api-clients/the-odds-api.ts`
2. Port odds fetching
3. Add caching layer
4. Add to API route data fetching

---

## Component Inventory

### Installed but Unused ✅
| Component | Purpose | Status | Integration Needed |
|-----------|---------|--------|-------------------|
| `InlineCitation` | Source attribution | Installed | Parse citations from LLM, render with hover cards |
| `Suggestion` | Welcome screen prompts | Partial use | Add as follow-up suggestions below responses |

### Already in Use ✅
| Component | Purpose | File |
|-----------|---------|------|
| `Conversation` | Chat container | `app/page.tsx` |
| `Message` | Chat bubbles | `app/page.tsx` |
| `Response` | Markdown renderer | `app/page.tsx` |
| `PromptInput` | User input | `app/page.tsx` |

### Not Needed (CLI-Specific)
- Python CLI interaction
- Terminal output formatting
- Manual data aggregator calls

---

## Implementation Roadmap

### Phase 1: API Clients (High Priority)
**Goal:** Port all data sources from Python to TypeScript

1. **API-Football Client** `lib/api-clients/api-football.ts`
   - Player stats endpoint
   - Injuries endpoint
   - TypeScript types
   - Caching layer

2. **TheSportsDB Client** `lib/api-clients/thesportsdb.ts`
   - Standings endpoint
   - Recent results endpoint
   - Team form endpoint
   - H2H endpoint
   - TypeScript types
   - Caching layer

3. **The Odds API Client** `lib/api-clients/the-odds-api.ts`
   - Betting odds endpoint
   - TypeScript types
   - Caching layer

**Files to create:** 3 new API clients
**Estimated effort:** 2-3 hours (using Python code as reference)

---

### Phase 2: Data Integration (High Priority)
**Goal:** Populate all data fields in API route

1. **Update API Route** `app/api/query/route.ts`
   - Import all API clients
   - Call all fetch methods in parallel
   - Populate `sports_events` array (standings + results + form)
   - Populate `player_stats` array
   - Add betting odds to context
   - Add injuries to context
   - Add H2H records to context

**Files to modify:** 1 (route.ts)
**Estimated effort:** 1 hour

---

### Phase 3: Source Attribution (Medium Priority)
**Goal:** Display citations in UI

1. **Citation Parser** `lib/utils/parse-citations.ts`
   - Parse LLM responses for citation markers
   - Extract source info (type, URL if applicable)
   - Convert to React component props

2. **Response Renderer Update** `components/ui/shadcn-io/ai/response.tsx`
   - Integrate citation parser
   - Render `InlineCitation` components inline
   - Show hover cards with source details

**Files to create:** 1 parser utility
**Files to modify:** 1 (response.tsx)
**Estimated effort:** 2 hours

---

### Phase 4: Article URLs (Low Priority)
**Goal:** Show clickable Kicker article links

1. **Article Link Component** (reuse `InlineCitation` or create custom)
   - Render after AI responses
   - Filter for relevance (don't show unrelated)
   - Format: "📰 Related from Kicker: • [Title] → [URL]"

2. **Response Display Update** `app/page.tsx`
   - Show article links section after assistant messages
   - Pass Kicker articles from data context

**Files to modify:** 1 (page.tsx or response.tsx)
**Estimated effort:** 1 hour

---

### Phase 5: Follow-up Suggestions (Low Priority)
**Goal:** Proactive user engagement

1. **System Prompt Update** `lib/prompts.ts`
   - Add follow-up requirement (already exists, just not enforced)
   - Context-aware suggestion templates

2. **Suggestion Renderer** `app/page.tsx`
   - Parse follow-up from LLM responses
   - Render `Suggestion` buttons below assistant messages
   - Handle click to submit as new query

**Files to modify:** 1 (page.tsx)
**Estimated effort:** 1-2 hours

---

## Testing Requirements

### API Integration Tests
- [ ] API-Football client fetches player stats correctly
- [ ] TheSportsDB client fetches standings correctly
- [ ] The Odds API client fetches odds correctly
- [ ] Caching works for all clients (6-hour TTL)
- [ ] API route populates all data fields

### UI Component Tests
- [ ] InlineCitation renders hover cards
- [ ] Citations parse correctly from LLM responses
- [ ] Article URLs display and are clickable
- [ ] Follow-up suggestions render and are clickable
- [ ] Bilingual support works for all new features

### E2E Tests
- [ ] User asks about player stats → Gets stats with citations
- [ ] User asks about standings → Gets table with citations
- [ ] User sees related Kicker articles after response
- [ ] User clicks follow-up suggestion → New query submitted
- [ ] All features work in both German and English

---

## Security Considerations

### API Keys Required
1. **API-Football** - `APIFOOTBALL_API_KEY`
2. **TheSportsDB** - Free tier (no key) or paid key
3. **The Odds API** - `ODDS_API_KEY`

### Rate Limiting
- Existing: Vercel KV (5 requests per 30 seconds)
- Consider: Per-API rate limiting to avoid exhausting quotas

### Data Validation
- Validate all API responses before passing to LLM
- Handle API errors gracefully (show cached data or user-friendly message)

---

## Success Metrics

### Feature Parity
- ✅ **Target:** 100% feature parity with CLI
- 📊 **Current:** ~25% (1 of 4 data sources)
- 🎯 **After Phase 1-2:** ~90% (all data sources + routing)
- 🎯 **After Phase 3-5:** 100% (citations + URLs + suggestions)

### User Experience
- Users see source attribution for all facts
- Users can click to read source articles
- Users get proactive follow-up suggestions
- Bilingual support maintained throughout

### Technical Quality
- All API clients use TypeScript with proper types
- Caching reduces API calls
- Security scanning passes (Semgrep)
- E2E tests cover all new features

---

## Next Steps

1. **Review audit with user** - Confirm priorities and approach
2. **Create Linear issues** - One per phase for tracking
3. **Start Phase 1** - Port API clients (highest impact)
4. **Semgrep scan after each phase** - Maintain security standards
5. **E2E tests after each phase** - Ensure nothing breaks

---

**Document Status:** 🟢 Complete
**Last Updated:** 2025-10-30
**Next Review:** After Phase 1 completion
