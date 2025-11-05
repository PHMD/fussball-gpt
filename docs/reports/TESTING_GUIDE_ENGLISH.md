# KSI Demo - English Testing Guide

**For non-German speakers who want to test the demo**

---

## Quick Start (Bilingual Mode)

### 1. Run the Bilingual Demo

```bash
source venv/bin/activate
python ksi_demo_bilingual.py --bilingual
```

The `--bilingual` flag enables **automatic English translation** of all German responses.

---

## What You'll See

### Example Session

```
KSI> 1
Question: Who is leading the Bundesliga table?
(German: Wer führt die Bundesliga-Tabelle an?)

Analyzing...

────────────────────────────────────────────────────────────────────────────
German Response: (3.42s)

Aktuell führt **Bayer Leverkusen** die Bundesliga mit **25 Punkten** an –
zwei Zähler vor dem FC Bayern München (23 Punkte). *Stand: nach dem letzten Spieltag.*

────────────────────────────────────────────────────────────────────────────
English Translation:

As it stands, **Bayer Leverkusen** top the Bundesliga table with **25 points**—
two points clear of FC Bayern Munich (23 points). *Status: after the latest matchday.*

────────────────────────────────────────────────────────────────────────────
```

---

## 10 Pre-Tested Example Queries

Just type the number (1-10) to test each query:

| # | English Question | What It Tests |
|---|---|---|
| **1** | Which Bundesliga games are happening this weekend? | Fixture listing, date handling |
| **2** | Who is leading the Bundesliga table? | Table standings, rankings |
| **3** | What is the result of Bayern Munich's last game? | Recent results, specific team |
| **4** | Which team has the best offense in the Bundesliga? | Statistical analysis, comparison |
| **5** | How is Bayer Leverkusen's form in recent games? | Form analysis, trend identification |
| **6** | Are there any current news about Bundesliga transfers? | News aggregation, transfer info |
| **7** | What are the most important sports news today? | General news, prioritization |
| **8** | Explain to me the current Champions League situation of German teams. | Complex analysis, multi-team context |
| **9** | Who are the top scorers in the Bundesliga? | Statistics, player rankings |
| **10** | What does the top of the table look like? | Table overview, standings summary |

---

## What to Test

### ✅ Quality Metrics (Expected: 7.33/10)

**German Journalism Tone:**
- [ ] Professional but friendly language
- [ ] No meta-explanations (doesn't say "based on the data provided...")
- [ ] Journalistic structure (headline-style emphasis)
- [ ] Uses German football terminology correctly

**Factual Accuracy:**
- [ ] Gets standings correct (Leverkusen 1st, Bayern 2nd)
- [ ] Reports scores accurately
- [ ] Names players/teams correctly
- [ ] Cites correct point totals

**Completeness:**
- [ ] Answers the full question
- [ ] Provides relevant context (not just raw data)
- [ ] Includes supporting details (e.g., "two points clear of...")
- [ ] Doesn't over-explain or under-explain

**Structure:**
- [ ] Well-formatted (uses bold, lists, sections)
- [ ] Easy to scan (bullet points, clear hierarchy)
- [ ] Consistent formatting across responses

---

### ✅ Speed Metrics (Expected: ~3.6s avg)

Bilingual mode will be **slower** because it makes TWO API calls:
1. German response: ~3-4 seconds
2. English translation: ~2-3 seconds
3. **Total: ~6-7 seconds** (this is expected)

For German-only speed testing, use:
```bash
python ksi_demo.py  # Original version, no translation
```

---

## Testing Workflow

### 1. Test All 10 Examples (5-10 minutes)

```bash
python ksi_demo_bilingual.py --bilingual

# Then type: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
```

**What to note:**
- Does the English translation make sense?
- Is the German response professional?
- Are facts accurate?
- Is the response complete?

---

### 2. Test Custom Queries (5 minutes)

You can type **English questions** and the demo will handle them:

```
KSI> Who scored the most goals this season?
```

The demo will:
1. Accept your English question
2. Generate a German response (based on German data)
3. Translate it back to English

**Try these:**
- "What happened in the last Bayern game?"
- "Who is winning the league?"
- "Any transfer news?"

---

### 3. Edge Cases to Test

**Query: Complex multi-part question**
```
KSI> Explain the top 3 teams and their recent form
```
Expected: Should handle 3+ entities in one response

**Query: Missing information**
```
KSI> What is the weather forecast for the next game?
```
Expected: Should say "Information not available in current data"

**Query: Ambiguous**
```
KSI> Who won?
```
Expected: Should ask for clarification or make reasonable assumption

---

## What Success Looks Like

### ✅ Pass Criteria

1. **All 10 examples work** (no crashes, no empty responses)
2. **Quality matches benchmark:**
   - Professional German journalism tone
   - Factually accurate (based on demo data)
   - Complete answers with context
   - Well-formatted output
3. **Speed acceptable:**
   - German-only: 3-5 seconds
   - Bilingual: 6-8 seconds
4. **English translations are readable** (you can understand what was said)

---

### ❌ Failure Modes to Watch For

**Critical (Should NOT happen):**
- Empty responses (like GPT-5 Nano failure)
- Crashes or API errors
- Completely incorrect facts (e.g., wrong team in 1st place)
- Responses in wrong language (English instead of German)

**Minor (Note but acceptable):**
- Slightly awkward phrasing in English translation
- Over-explanation on simple queries
- Formatting inconsistencies

---

## Comparison to Benchmark

**What the benchmark tested:**
- 8 different LLM models
- 10 German sports queries (same as this demo)
- 3-judge consensus evaluation
- Quality dimensions: German language, tone, accuracy, completeness, structure

**Mistral Large benchmark results:**
- **Quality:** 7.33/10 (2nd place, close to GPT-5 Mini's 7.44/10)
- **Speed:** 3.64s average (fastest among top-quality models)
- **Reliability:** 100% success rate (unlike GPT-5 Nano which failed catastrophically)

**Your testing goal:**
Verify that the demo **matches benchmark quality** (professional German journalism, accurate facts, ~7/10 subjective quality)

---

## Commands Summary

```bash
# Bilingual mode (for English speakers)
python ksi_demo_bilingual.py --bilingual

# German-only mode (for Kicker testing)
python ksi_demo.py

# Quick test (verifies API works)
python test_bilingual_demo.py

# See help
python ksi_demo_bilingual.py --help
```

---

## Troubleshooting

### "MISTRAL_API_KEY not found"
Make sure `.env` file exists with:
```
MISTRAL_API_KEY=your_key_here
```

### Translations seem off
- This is normal - translation adds interpretation
- Focus on German response quality (that's what Kicker users will see)
- English is for YOUR testing, not for production

### Slow responses (>10s bilingual)
- Check internet connection
- Expected: ~6-7s in bilingual mode
- If >10s consistently, may indicate API congestion

---

## What to Report

After testing, note:

1. **Quality Assessment (1-10):** How good are the responses?
2. **Speed:** Average response time you observed
3. **Failures:** Any queries that didn't work?
4. **Edge Cases:** Anything unexpected or interesting?
5. **Comparison to Expectations:** Does it feel like 7.33/10 quality?

**Example report:**
```
Tested all 10 examples in bilingual mode.

Quality: 7.5/10 subjective
- Professional tone ✅
- Accurate facts ✅
- Good formatting ✅
- Slightly verbose on #8 (Champions League)

Speed: 6.2s average (bilingual mode)
Failures: None
Edge cases: Handled ambiguous query well

Feels like benchmark quality. Ready for Kicker eval.
```

---

## Next Steps After Testing

1. **If quality acceptable:** Share with Kicker for evaluation
2. **If issues found:** Document specific problems for fixes
3. **If ready for production:** Proceed with roadmap Phase 2 (live data integration)

See `NEXT_STEPS_ROADMAP.md` for full development plan.
