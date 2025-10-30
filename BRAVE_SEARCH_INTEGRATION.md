# Brave Search API Integration

**Status**: ✅ Implemented (Oct 2025)
**Purpose**: Fallback for when RSS feeds have insufficient Bundesliga coverage

## What Was Implemented

### Tier 1: RSS Filtering (Active Now)
- ✅ 7 unique Bundesliga articles from 2 RSS feeds
- ✅ Content-based filtering (excludes NFL, NBA, other sports)
- ✅ Deduplication across feeds
- ✅ Zero cost

### Tier 2: Brave Search Fallback (Ready to Enable)
- ✅ Code implemented and tested
- ✅ Automatic triggering when RSS <5 articles
- ✅ Searches entire kicker.de archive
- ⏸️  Requires API key (not enabled yet)

## How It Works

```python
# In CLI main loop (cli.py:342-351)
data = self.refresh_data()  # Get RSS articles

# Automatic fallback
if len(data.news_articles) < 5 and self.aggregator.has_brave_search:
    brave_articles = self.aggregator.fetch_kicker_articles_brave(
        query=user_input,  # Use actual user query
        max_results=5
    )
    data.news_articles.extend(brave_articles)  # Augment context

# LLM sees combined pool (RSS + Brave)
response = self.llm.query(user_input, data, ...)
```

## Benefits

**1. Query-Specific Discovery**
- RSS: Generic "recent articles" (limited to last 20 from feed)
- Brave: Searches for user's actual query terms

**Example**:
- User: "What are the latest transfer rumors?"
- RSS: May have 0 transfer articles (just published today's news)
- Brave: Searches kicker.de archive for "transfer rumors" → finds relevant articles from past week

**2. Archive Access**
- RSS: Only last ~20 articles
- Brave: Entire kicker.de archive

**3. Better Coverage for Niche Queries**
- RSS: 7 Bundesliga articles (general coverage)
- Brave: Query-specific results (e.g., "Leverkusen tactics", "Bayern injury news")

## Setup Instructions

### Step 1: Get API Key (Free)
1. Visit: https://brave.com/search/api/
2. Sign up for free tier
3. Get API key (2,000 requests/month, 1 req/sec)

### Step 2: Configure
Add to `.env` file:
```bash
BRAVE_SEARCH_API_KEY=your_key_here
```

### Step 3: Test
```bash
source venv/bin/activate
python test_brave_search.py
```

Expected output:
```
✅ Brave Search API configured
🔍 Query: Harry Kane Bayern München
✅ Found 5 articles:
1. Kane's Record-Breaking Start at Bayern
   URL: https://www.kicker.de/...
   Snippet: Harry Kane has made an immediate impact...
```

## Cost Analysis

**Free Tier**:
- 2,000 requests/month = ~67 queries/day
- 1 request/second rate limit
- **Cost**: $0

**Paid Tier** (if needed):
- $5 per 1,000 requests
- At 100K queries/month: $500/month
- At 10K queries/month: $50/month

**When to upgrade**:
- Beta testing: Free tier sufficient (2K req/month)
- Production: Depends on traffic (monitor usage)

## Comparison Matrix

| Metric | RSS Only | RSS + Brave Search |
|--------|----------|-------------------|
| Articles | 7 Bundesliga | 7 + up to 5 more |
| Coverage | Recent only | Full archive |
| Query-specific | ❌ No | ✅ Yes |
| Latency | 0ms (cached) | +500ms (search) |
| Cost | Free | Free (2K/mo) |

## Testing Without API Key

The system works without Brave Search:
- RSS provides baseline 7 articles
- Brave Search simply won't activate
- No errors, graceful degradation

Test current RSS-only setup:
```bash
source venv/bin/activate
python test_tier1_filtering.py
```

## When Brave Search Triggers

**Triggers** (automatic):
- `if len(data.news_articles) < 5`

**Current state**:
- RSS typically provides 7 articles
- Brave Search won't trigger in normal operation
- Acts as safety net for sparse days

**To test triggering**:
Modify threshold in `cli.py:344`:
```python
# Change from <5 to >0 to always trigger
if len(data.news_articles) > 0 and self.aggregator.has_brave_search:
```

## Architecture Notes

**Why at CLI level, not data aggregator?**
- User query needed for Brave Search
- `aggregate_all()` runs before query known
- CLI has both query and data context

**Deduplication**:
- Brave Search returns different URLs than RSS
- LLM sees combined pool
- LLM naturally picks most relevant (doesn't show duplicates)

## Next Steps

**For Beta**:
1. Test with current RSS-only (7 articles)
2. Get Brave API key if 7 articles feels insufficient
3. Monitor article relevance in persona tests

**For Production**:
1. Evaluate Brave Search usage in beta
2. Consider paid tier if free exhausted
3. Alternative: Full CMS integration (per architecture doc)

## Related Files

- `data_aggregator.py:177-241` - Brave Search implementation
- `cli.py:342-351` - Automatic fallback logic
- `.env.example:22-26` - Configuration example
- `test_brave_search.py` - Test script
