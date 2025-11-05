# KSI Demo - Quick Start

**TL;DR: Working German sports journalism assistant powered by Mistral Large**

---

## 🚀 For English Speakers (YOU)

### ⭐ RECOMMENDED: Enhanced Demo with Model Switching

```bash
source venv/bin/activate
python ksi_demo_enhanced.py --bilingual
```

**New features:**
- Switch between 8 different LLM models with `/model <name>`
- Compare models side-by-side on same queries
- Show benchmark stats with `/benchmark`
- Track session stats with `/stats`
- Toggle translation with `/translate`

**📖 Command Reference:** See `COMMANDS_REFERENCE.md` for all slash commands

### Standard Demo (Simple Version)

```bash
source venv/bin/activate
python ksi_demo_bilingual.py --bilingual
```

### Then type: `1`

You'll see:
- **German response** (what Kicker users would see)
- **English translation** (so you can evaluate quality)

### Try all 10 examples:

Just type numbers 1-10 to test each pre-validated query.

**Full testing guide:** `TESTING_GUIDE_ENGLISH.md`

---

## 🎯 For Kicker Team (German Speakers)

### Run this command:

```bash
source venv/bin/activate
python ksi_demo.py
```

### Then type: `1`

You'll see professional German sports journalism responses based on current Bundesliga data.

**Full demo guide:** `README_DEMO.md`

---

## ✅ What You're Testing

**Mistral Large** - Selected from 8-model benchmark:
- **Quality:** 7.33/10 (professional German journalism)
- **Speed:** ~3.6s average
- **Reliability:** 100% success rate

**What was tested:**
- 8 different LLM models
- 10 German sports queries
- 3-judge consensus evaluation
- Fair testing protocol (no reasoning mode bias)

**Why Mistral Large won:**
- Best balance of quality and speed
- No catastrophic failures (unlike GPT-5 Nano)
- Professional journalism tone
- Accurate facts, complete answers

---

## 📊 Expected Results

### ✅ Pass Criteria

- All 10 examples work (no crashes)
- Professional German journalism tone
- Factually accurate (based on demo data)
- Complete answers with context
- Well-formatted output
- Speed: 3-5s (German-only), 6-8s (bilingual)

### ❌ Watch For

- Empty responses (should NOT happen)
- Crashes or API errors
- Incorrect facts
- Wrong language output

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `ksi_demo_bilingual.py` | **Start here** - Bilingual demo for English speakers |
| `ksi_demo.py` | German-only demo for Kicker team |
| `TESTING_GUIDE_ENGLISH.md` | Complete testing instructions |
| `README_DEMO.md` | Full demo documentation |
| `FINAL_LLM_BENCHMARK_REPORT.md` | Complete benchmark results |
| `NEXT_STEPS_ROADMAP.md` | Development roadmap |

---

## 🔧 Quick Test (30 seconds)

```bash
# Verify everything works
source venv/bin/activate
python test_bilingual_demo.py
```

Expected output:
```
✅ German Response:
Aktuell führt **Bayer Leverkusen** die Bundesliga mit **25 Punkten** an...

✅ English Translation:
As it stands, **Bayer Leverkusen** top the Bundesliga table with **25 points**...

✅ Bilingual demo test successful!
```

---

## ❓ FAQ

**Q: I don't speak German, how do I test?**
A: Use `python ksi_demo_bilingual.py --bilingual` - it translates everything to English.

**Q: How long does testing take?**
A: 5-10 minutes to test all 10 examples.

**Q: What if I find issues?**
A: Note them down (quality, speed, specific failures) and report back.

**Q: Is this production-ready?**
A: This is a **prototype** with static data. Next step: live Bundesliga data integration.

---

## 🎬 Next Steps

1. **Test the demo** (5-10 min)
2. **Review benchmark report** (`FINAL_LLM_BENCHMARK_REPORT.md`)
3. **Check roadmap** (`NEXT_STEPS_ROADMAP.md`)
4. **Decide:** Continue to Phase 2 (live data) or iterate on prototype?

---

**Project Status:** Demo ready for evaluation
**Model:** Mistral Large (benchmark-validated)
**Date:** October 2025
