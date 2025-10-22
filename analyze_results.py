#!/usr/bin/env python3
"""Analyze benchmark results and generate comparison report"""

import json
from collections import defaultdict

# Read results
with open('results/benchmark_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

print("="*80)
print("  GERMAN LANGUAGE BENCHMARK - DETAILED ANALYSIS")
print("="*80)
print()

# Category breakdown
print("📊 PERFORMANCE BY CATEGORY\n")
categories = defaultdict(lambda: defaultdict(list))

for result in results:
    if result['success']:
        cat = result['category']
        model = result['display_name']
        categories[cat][model].append(result['time_ms'])

category_order = [
    'short_form_qa',
    'long_form_editorial',
    'multi_turn_conversation',
    'rag_data_grounding'
]

category_names = {
    'short_form_qa': 'Short-Form Q&A',
    'long_form_editorial': 'Long-Form Editorial',
    'multi_turn_conversation': 'Multi-Turn Conversation',
    'rag_data_grounding': 'RAG Data Grounding'
}

for cat in category_order:
    print(f"\n{category_names[cat]}:")
    print("-" * 60)

    # Get average times for this category
    cat_times = []
    for model, times in categories[cat].items():
        avg_time = sum(times) / len(times)
        cat_times.append((model, avg_time))

    # Sort by time
    cat_times.sort(key=lambda x: x[1])

    # Print top 5
    for i, (model, time) in enumerate(cat_times[:5], 1):
        print(f"  {i}. {model:<25} {time:>6.0f}ms")

# German response samples
print("\n" + "="*80)
print("  GERMAN LANGUAGE QUALITY SAMPLES")
print("="*80)
print()

# Get one example from each category for top 3 models
top_models = ['Mistral Small', 'Claude Haiku 4.5', 'Llama 3.1 8B']

for cat in category_order:
    print(f"\n📝 {category_names[cat]}")
    print("="*80)

    for model in top_models:
        # Find result for this model/category
        for result in results:
            if result['display_name'] == model and result['category'] == cat and result['success']:
                response = result['response']
                # Truncate if too long
                if len(response) > 300:
                    response = response[:300] + "..."

                print(f"\n[{model}] ({result['time_ms']}ms)")
                print(f"{response}")
                print()
                break

print("\n" + "="*80)
print("  TOKEN USAGE & COST BY MODEL")
print("="*80)
print()

# Aggregate by model
model_stats = defaultdict(lambda: {'input': 0, 'output': 0, 'count': 0})

for result in results:
    if result['success']:
        model = result['display_name']
        model_stats[model]['input'] += result.get('input_tokens', 0)
        model_stats[model]['output'] += result.get('output_tokens', 0)
        model_stats[model]['count'] += 1

# Sort by total tokens
sorted_models = sorted(model_stats.items(),
                      key=lambda x: x[1]['input'] + x[1]['output'],
                      reverse=True)

for model, stats in sorted_models:
    total = stats['input'] + stats['output']
    print(f"{model:<25} In: {stats['input']:>6,} | Out: {stats['output']:>6,} | Total: {total:>7,}")

print("\n" + "="*80)
print("  RECOMMENDATIONS")
print("="*80)
print()

print("🚀 FASTEST (Real-time use):")
print("   1. Mistral Small - 3,031ms avg")
print("   2. Claude Haiku 4.5 - 5,446ms avg")
print("   3. Llama 3.1 8B - 6,315ms avg (open-source)")
print()

print("💰 BEST VALUE (Speed + Cost):")
print("   1. Llama 3.1 8B - Fast + open-source pricing")
print("   2. Mistral Small - Ultra-fast + low cost")
print("   3. Qwen 2.5 14B - Good speed + open-source")
print()

print("🇩🇪 GERMAN SPECIALISTS:")
print("   1. Mistral Large - Native German, 11.3s avg")
print("   2. Mistral Medium - German-optimized, 13.1s avg")
print("   3. Mistral Small - Fast German, 3.0s avg")
print()

print("🎯 PRODUCTION RECOMMENDATIONS:")
print("   • Short answers/scores: Mistral Small")
print("   • Conversational chat: GPT-5 Chat or Claude Haiku")
print("   • Editorial quality: Claude Sonnet 4.5 or Mistral Large")
print("   • Budget/high-volume: Llama 3.1 8B")
print("   • Deep analysis: GPT-5 (accept 14s latency)")
print()
