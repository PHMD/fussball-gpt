# KSI Demo - Kicker Sports Intelligence

**Powered by Mistral Large**
- Quality: 7.33/10 (benchmark-validated)
- Speed: ~3.6 seconds average response
- Language: German sports journalism

---

## Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the project directory
cd /Users/patrickmeehan/knowledge-base/projects/ksi_prototype

# Activate virtual environment
source venv/bin/activate

# Install requirements (if not already done)
pip install mistralai python-dotenv
```

### 2. Run the Demo

**For German speakers (Kicker team):**
```bash
python ksi_demo.py
```

**For English speakers (testing/evaluation):**
```bash
python ksi_demo_bilingual.py --bilingual
```

The bilingual version automatically translates all German responses to English, making it easy to evaluate quality without speaking German.

**📖 English Testing Guide:** See `TESTING_GUIDE_ENGLISH.md` for complete testing instructions.

### 3. Try Example Queries

The demo includes 10 pre-tested queries. You can:
- Type a number (1-10) to use an example query
- Type your own German sports question
- Type `beispiele` or `examples` to see examples again
- Type `quit` to exit

---

## Example Session

```
KSI> 1
Frage: Welche Bundesliga-Spiele stehen dieses Wochenende an?

Analysiere...

────────────────────────────────────────────────────────────────────────────
Antwort: (3.42s)

Am kommenden Wochenende stehen spannende Bundesliga-Spiele an:

**Freitag, 20:30**
- Borussia Dortmund vs. FC St. Pauli

**Samstag, 15:30**
- Bayern München vs. Union Berlin
- VfB Stuttgart vs. Holstein Kiel

**Samstag, 18:30**
- Bayer Leverkusen vs. Eintracht Frankfurt (Spitzenspiel!)

**Sonntag, 15:30**
- RB Leipzig vs. SC Freiburg

**Sonntag, 17:30**
- VfL Wolfsburg vs. FC Augsburg

Besonders interessant ist das Duell zwischen Tabellenführer Leverkusen und
Frankfurt am Samstagabend.
────────────────────────────────────────────────────────────────────────────
```

---

## What's Inside

### Realistic Bundesliga Data

The demo includes current (example) data:
- League standings (Top 5)
- Recent match results
- Upcoming fixtures
- Top scorers
- Transfer news
- Champions League standings

### Benchmark-Proven Quality

This demo uses **Mistral Large**, selected from an 8-model evaluation:
- Tested against Claude Sonnet/Haiku, GPT-5 variants, Mistral Small
- 3-judge consensus evaluation
- Fair testing protocol validated

**Why Mistral Large?**
- Best balance of quality (7.33/10) and speed (3.64s)
- Consistent performance across all test queries
- No reliability issues (unlike GPT-5 Nano which failed on complex queries)

---

## 10 Example Queries

1. Welche Bundesliga-Spiele stehen dieses Wochenende an?
2. Wer führt die Bundesliga-Tabelle an?
3. Was ist das Ergebnis des letzten Bayern München Spiels?
4. Welches Team hat die beste Offensive in der Bundesliga?
5. Wie ist die Form von Bayer Leverkusen in den letzten Spielen?
6. Gibt es aktuelle Nachrichten über Bundesliga-Transfers?
7. Was sind die wichtigsten Sportnachrichten heute?
8. Erkläre mir die aktuelle Champions League Situation deutscher Teams.
9. Wer sind die Top-Torjäger der Bundesliga?
10. Wie sieht die Spitzengruppe der Tabelle aus?

---

## Technical Details

### Model Configuration
- **Model:** mistral-large-latest
- **Max Tokens:** 2000
- **Temperature:** 0.7 (balanced creativity)
- **System Prompt:** Optimized for kicker.de journalism standard

### Data Source
Currently uses static example data. In production:
- Live Bundesliga API integration
- Real-time score updates
- News feed aggregation
- Match statistics API

---

## Troubleshooting

### "MISTRAL_API_KEY not found"
Make sure `.env` file exists in project root with:
```
MISTRAL_API_KEY=your_key_here
```

### "Module 'mistralai' not found"
Install the Mistral SDK:
```bash
pip install mistralai
```

### Slow responses (>10s)
- Check internet connection
- Mistral API may be under load
- Expected: 3-4 seconds, acceptable: up to 8 seconds

---

## What's Next?

### Immediate Next Steps
1. **Get Feedback:** Try the demo, note what works and what doesn't
2. **Identify Gaps:** What queries don't work well?
3. **Data Needs:** What live data feeds are required?

### Future Enhancements
1. **Live Data Integration:** Real Bundesliga API
2. **Web API:** RESTful API for frontend integration
3. **Streaming:** Real-time response streaming
4. **Caching:** Common query optimization
5. **Multi-turn:** Conversation support

See `NEXT_STEPS_ROADMAP.md` for full development plan.

---

## Benchmark Report

For complete evaluation details, see:
- **FINAL_LLM_BENCHMARK_REPORT.md** - Comprehensive 8-model comparison
- **results/** directory - Raw evaluation data

**Key Findings:**
- Mistral Large: Best production choice (7.33/10 @ 3.64s)
- GPT-5 Mini: Highest quality but slow (7.44/10 @ 11.17s)
- GPT-5 Nano: ❌ Not recommended (catastrophic failure on complex queries)

---

## Contact

**Project:** KSI (Kicker Sports Intelligence) Prototype
**Date:** October 2025
**Status:** Demo - ready for Kicker evaluation

For questions or feedback, contact the development team.
