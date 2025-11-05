# Setting Up The Odds API (Issue #8)

## Overview

The Odds API provides pre-match betting odds for Bundesliga fixtures. This significantly improves the **Betting Enthusiast** persona quality from 7-9/10 to 9.5-10/10.

## Free Tier Details

- **Requests:** 500/month
- **Cost:** Free (credit card required for registration)
- **Coverage:** Bundesliga + 80+ sports worldwide
- **Odds format:** Decimal (European style)
- **Update frequency:** Real-time

## Setup Steps

### 1. Get Free API Key

1. Visit: https://the-odds-api.com/
2. Click "Get Started Free" or "Sign Up"
3. Create account (requires email + credit card for verification)
4. Navigate to dashboard: https://dash.the-odds-api.com/
5. Copy your API key

### 2. Add to Environment

Edit `.env` file and add:

```bash
ODDS_API_KEY=your_actual_api_key_here
```

### 3. Test Integration

```bash
python test_betting_odds.py
```

Expected output:
- Fetches odds for upcoming Bundesliga fixtures
- Shows quota remaining (should be ~500 on first run)
- LLM references odds in betting analysis

## Data Format

Odds are displayed in LLM context as:

```
=== BETTING ODDS (Upcoming Fixtures) ===
⚠️  Odds are for entertainment purposes only

Bayern München vs Borussia Dortmund (25.10 15:30)
  Quoten: Heim 1.50 | Unentschieden 4.20 | Auswärts 7.00
  Quelle: Bet365

RB Leipzig vs Bayer Leverkusen (26.10 18:30)
  Quoten: Heim 2.10 | Unentschieden 3.60 | Auswärts 3.40
  Quelle: Bet365
```

## Caching

- **Cache duration:** 24 hours
- **Cache file:** `cache/betting_odds.json`
- **Reason:** Odds don't change frequently for pre-match; conserves API quota

## Rate Limiting

The API returns usage headers:
- `x-requests-remaining`: Quota left this month
- `x-requests-used`: Requests consumed
- `x-requests-last`: Timestamp of last request

If you hit the 500/month limit:
- API returns 429 status code
- System gracefully uses cached data
- Quota resets monthly

## Quota Management

**Monthly usage estimate (with caching):**

- Data aggregation runs: ~4x per day (testing/development)
- Odds fetch: 1x per 24 hours (cached)
- Monthly requests: ~30 (well under 500 limit)

**Recommendation:** With 24-hour caching, free tier is sufficient even with heavy testing.

## Expected Impact

**Before (without odds):**
- Betting Enthusiast: 7-9/10
- Lacks critical betting context
- Cannot answer value bet questions

**After (with odds):**
- Betting Enthusiast: 9.5-10/10
- Provides odds-based analysis
- Identifies value bets based on form + odds
- Professional betting recommendations

## Troubleshooting

### "ODDS_API_KEY not found"
- Check `.env` file exists
- Verify key is added correctly
- Restart CLI after adding key

### "Invalid API key" (401 error)
- Verify key copied correctly (no extra spaces)
- Check if key is active on dashboard

### "Rate limit exceeded" (429 error)
- Check usage on dashboard
- Wait for monthly reset
- Consider clearing cache for fresh data

### No odds returned
- Bundesliga may be off-season (summer break)
- API may have limited coverage during international breaks
- Check API status: https://the-odds-api.com/api-status

## Alternative: Without Odds API

If you don't want to set up The Odds API:

- System works fine without it
- Shows "0 odds" in data summary
- Betting persona will be 7-9/10 instead of 9.5-10/10
- Other personas unaffected

## Legal Disclaimer

Betting odds are provided for **entertainment and informational purposes only**.

This is clearly stated in the LLM context:
> ⚠️  Odds are for entertainment purposes only

Users should:
- Comply with local gambling laws
- Use odds responsibly
- Not rely solely on AI for betting decisions
- Seek professional advice for gambling issues
