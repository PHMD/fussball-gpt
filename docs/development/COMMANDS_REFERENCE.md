# KSI Demo - Slash Commands Reference

**Enhanced demo with model switching and testing tools**

---

## Quick Start

```bash
source venv/bin/activate
python ksi_demo_enhanced.py --bilingual
```

---

## Available Commands

### `/model <name>`
**Switch between LLM models**

```
KSI> /model gpt-5-mini
Switched to GPT-5 Mini
```

**Available models:**
- `mistral-large` - Recommended (7.33/10 @ 3.64s)
- `mistral-small` - Fast & cheap (6.79/10 @ 2.67s)
- `gpt-5` - Base GPT-5 (7.25/10 @ 13.17s)
- `gpt-5-mini` - Highest quality (7.44/10 @ 11.17s)
- `gpt-5-chat` - Fast GPT-5 (7.18/10 @ 4.02s)
- `gpt-5-nano` - ⚠️ **Unreliable** (6.39/10, fails on complex queries)
- `claude-sonnet` - Claude Sonnet 4.5 (7.22/10 @ 7.33s)
- `claude-haiku` - Fast Claude (6.87/10 @ 3.42s)

**Use case:** Compare models side-by-side on same query

---

### `/models`
**List all available models with benchmark scores**

```
KSI> /models

Available Models:

   ✅ gpt-5-mini            GPT-5 Mini                   7.44/10 @ 11.17s
⭐ ✅ mistral-large         Mistral Large                7.33/10 @ 3.64s
   ✅ gpt-5                 GPT-5                        7.25/10 @ 13.17s
   ✅ claude-sonnet         Claude Sonnet 4.5            7.22/10 @ 7.33s
   ✅ gpt-5-chat            GPT-5 Chat                   7.18/10 @ 4.02s
   ✅ claude-haiku          Claude Haiku 3.5             6.87/10 @ 3.42s
   ✅ mistral-small         Mistral Small                6.79/10 @ 2.67s
   ✅ gpt-5-nano            GPT-5 Nano                   6.39/10 @ 14.10s ⚠️ Known to fail
```

**Legend:**
- ⭐ = Currently active model
- ✅ = Available (API key configured)
- ❌ = Unavailable (missing API key)

---

### `/stats`
**Show session statistics**

```
KSI> /stats

Session Statistics:

  Queries: 5
  Average Response Time: 4.23s
  Total Time: 21.15s
  Current Model: Mistral Large
  Bilingual Mode: On
```

**Use case:** Track performance during testing session

---

### `/language <de|en>`
**Switch output language**

```
KSI> /language en
Output language switched to English

KSI> 1
# Now gets English response directly (no translation needed)

KSI> /language de
Output language switched to German
```

**Languages:**
- `de` - German (default, matches benchmark testing)
- `en` - English (for testing if models are better in English)

**Use cases:**
- **Compare language quality:** Test if model produces better journalism in English vs German
- **No translation overhead:** Get English responses directly (~3-4s vs 6-7s with translation)
- **Validate multilingual capability:** Confirm model can handle both languages well

**Note:** Benchmark testing was done in German, so German responses match the validated quality scores (7.33/10 for Mistral Large, etc.)

---

### `/translate`
**Toggle English translation on/off**

```
KSI> /translate
Translation enabled

KSI> /translate
Translation disabled
```

**Use case:**
- Turn on for English testing
- Turn off for speed testing (skips translation step)

---

### `/benchmark`
**Show benchmark comparison table**

```
KSI> /benchmark

Benchmark Results (8-Model Comparison):

Model                     Quality      Speed      Status
──────────────────────────────────────────────────────────────────────
GPT-5 Mini                ███████░░░ 7.44/10  11.17s   ✅
Mistral Large             ███████░░░ 7.33/10  3.64s    ✅
GPT-5                     ███████░░░ 7.25/10  13.17s   ✅
Claude Sonnet 4.5         ███████░░░ 7.22/10  7.33s    ✅
GPT-5 Chat                ███████░░░ 7.18/10  4.02s    ✅
Claude Haiku 3.5          ██████░░░░ 6.87/10  3.42s    ✅
Mistral Small             ██████░░░░ 6.79/10  2.67s    ✅
GPT-5 Nano                ██████░░░░ 6.39/10  14.10s   ❌ Not recommended

Recommendation: Mistral Large (best balance of quality & speed)
See FINAL_LLM_BENCHMARK_REPORT.md for full details
```

**Use case:** Quick reference during model comparison

---

### `/clear`
**Clear screen**

```
KSI> /clear
```

**Use case:** Clean up terminal for screenshots or fresh testing

---

### `/help`
**Show commands and examples**

```
KSI> /help
```

Displays:
- 10 example queries
- All slash commands
- Usage instructions

---

### `/quit`
**Exit demo**

```
KSI> /quit
Auf Wiedersehen! (Goodbye!)
```

Alternative: Type `quit`, `exit`, or `q`

---

## Common Workflows

### 1. Model Comparison Testing

**Goal:** Test same query across multiple models

```bash
KSI> /model mistral-large
KSI> 1                        # "Which games this weekend?"
# Note the response quality and speed

KSI> /model gpt-5-mini
KSI> 1                        # Same query
# Compare quality/speed

KSI> /model claude-sonnet
KSI> 1                        # Same query
# Compare again

KSI> /stats                   # See average speeds
```

**Use case:** Validate benchmark findings with your own testing

---

### 2. Speed Testing (No Translation)

**Goal:** Test pure model speed without translation overhead

```bash
KSI> /translate              # Turn OFF translation
KSI> /model mistral-large
KSI> 1
# Should complete in ~3-4 seconds

KSI> /model gpt-5-mini
KSI> 1
# Should complete in ~11 seconds

KSI> /stats                  # Verify avg speeds match benchmark
```

**Use case:** Confirm benchmark speed claims

---

### 3. Quality Testing (With Translation)

**Goal:** Evaluate German journalism quality as English speaker

```bash
KSI> /translate              # Turn ON translation
KSI> /model mistral-large
KSI> 1

# Evaluate:
# - Does German look professional?
# - Is English translation coherent?
# - Are facts accurate?
# - Is formatting good?

KSI> /model gpt-5-mini
KSI> 1
# Compare quality difference
```

**Use case:** Subjective quality evaluation

---

### 4. Edge Case Testing

**Goal:** Test GPT-5 Nano failure mode

```bash
KSI> /model gpt-5-nano
KSI> 8                       # Champions League query (complex)
# Expected: May fail or return empty/poor response

KSI> /model mistral-large
KSI> 8                       # Same query
# Expected: Should succeed
```

**Use case:** Validate benchmark failure findings

---

### 5. Production Speed Testing

**Goal:** Verify bilingual mode performance

```bash
KSI> /translate              # Ensure ON
KSI> /model mistral-large
KSI> 1

# Expected timing:
# - German response: ~3-4s
# - Translation: ~2-3s
# - Total: ~6-7s

KSI> /stats                  # Verify average matches expectation
```

**Use case:** Confirm bilingual mode is production-viable

---

### 6. Language Comparison Testing

**Goal:** Test if models perform better in English vs German

```bash
# Test in German (benchmark language)
KSI> /language de
KSI> /model mistral-large
KSI> 8                       # Complex Champions League query
# Note quality and completeness

# Test same query in English
KSI> /language en
KSI> 8                       # Same query number
# Compare: Is English better/worse/same?

# Try with different model
KSI> /model gpt-5-mini
KSI> /language de
KSI> 8                       # German
KSI> /language en
KSI> 8                       # English

KSI> /stats                  # Speeds should be similar
```

**Use case:**
- Determine if English prompts get better responses
- Validate German benchmark scores are representative
- Consider if product should support English output

**Expected finding:** Most models trained primarily on English may perform slightly better in English, but German quality should still be good (7+ for top models).

---

## API Key Requirements

The demo auto-detects available API keys from `.env`:

```bash
# Mistral models (mistral-large, mistral-small)
MISTRAL_API_KEY=your_key_here

# OpenAI models (gpt-5, gpt-5-mini, gpt-5-chat, gpt-5-nano)
OPENAI_API_KEY=your_key_here

# Anthropic models (claude-sonnet, claude-haiku)
ANTHROPIC_API_KEY=your_key_here
```

**You need at least ONE** API key to run the demo.

Models with missing API keys will show `❌` in `/models` list.

---

## Tips & Tricks

**Quick model switching:**
```
KSI> /model mistral-large
KSI> 1
KSI> /model gpt-5-mini
KSI> 1
KSI> /stats
```

**Test all examples on one model:**
```
KSI> /model mistral-large
KSI> 1
KSI> 2
KSI> 3
...
KSI> 10
KSI> /stats
```

**Speed comparison:**
```
KSI> /translate          # Turn off
KSI> /model mistral-small
KSI> 1                   # Fastest (2.67s)
KSI> /model mistral-large
KSI> 1                   # Balanced (3.64s)
KSI> /model gpt-5-mini
KSI> 1                   # Slow but best quality (11.17s)
```

**Quality comparison:**
```
KSI> /translate          # Turn on (to read responses)
KSI> /model gpt-5-mini   # Highest quality (7.44/10)
KSI> 8                   # Complex Champions League query
KSI> /model mistral-large # Recommended (7.33/10)
KSI> 8                   # Same query
# Compare: Is 0.11 quality difference worth 3x slower speed?
```

---

## Keyboard Shortcuts

- **Ctrl+C** - Exit demo
- **Ctrl+D** - Exit demo (Unix/Mac)
- **Up Arrow** - Previous command (terminal history)

---

## Troubleshooting

**"Model not available (missing API key)"**
- Add the required API key to `.env` file
- Restart the demo

**"Unknown model: xyz"**
- Use `/models` to see exact model names (lowercase, hyphenated)

**Translation errors**
- Translation uses same model as query
- If model fails, translation will also fail
- Try different model with `/model <name>`

**Slow responses**
- Check `/benchmark` for expected speeds
- Some models are inherently slow (GPT-5 base: 13s)
- Network latency may add 1-2s

---

## What's Next?

After testing with slash commands:
1. Review `FINAL_LLM_BENCHMARK_REPORT.md` for detailed findings
2. Check `NEXT_STEPS_ROADMAP.md` for development plan
3. Decide: Stick with Mistral Large or explore alternatives?

**Production recommendation:** Mistral Large (7.33/10 @ 3.64s)
- Best quality/speed balance
- No catastrophic failures
- Consistent performance
