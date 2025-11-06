#!/usr/bin/env tsx
/**
 * Quick validation script for query classifier
 * Run with: npx tsx scripts/test-classifier.ts
 */

import { classifyQuery, getRequiredDataSources, estimateTokenSavings } from '../lib/query-classifier';
import type { QueryCategory } from '../lib/query-classifier';

// Test cases from Linear issue
const testCases: Array<{ query: string; expected: QueryCategory; description: string }> = [
  // News queries
  { query: "What's the latest Bundesliga news?", expected: 'news', description: 'Latest news request' },
  { query: 'Tell me about transfers', expected: 'news', description: 'Transfer news' },
  { query: 'Any breaking news today?', expected: 'news', description: 'Breaking news' },
  { query: 'What happened in Bundesliga this weekend?', expected: 'news', description: 'Recent news query' },

  // Player queries
  { query: 'Is Neuer injured?', expected: 'player', description: 'Player injury' },
  { query: "Who's the top scorer?", expected: 'player', description: 'Top scorer' },
  { query: 'How is Kane performing?', expected: 'player', description: 'Player performance' },
  { query: 'Tell me about Musiala stats', expected: 'player', description: 'Player stats' },

  // Match queries
  { query: 'When does Bayern play next?', expected: 'match', description: 'Next fixture' },
  { query: 'What are the odds for Dortmund?', expected: 'match', description: 'Betting odds' },
  { query: 'Bayern vs Leipzig result', expected: 'match', description: 'Match result' },
  { query: 'Show me upcoming fixtures', expected: 'match', description: 'Fixture schedule' },

  // Standings queries
  { query: 'Show me the table', expected: 'standings', description: 'League table' },
  { query: "Who's in first place?", expected: 'standings', description: 'First place query' },
  { query: 'Current Bundesliga standings', expected: 'standings', description: 'Current standings' },
  { query: 'Where is Frankfurt in the table?', expected: 'standings', description: 'Team position' },

  // Meta queries
  { query: 'How does this app work?', expected: 'meta', description: 'App functionality' },
  { query: 'What can you do?', expected: 'meta', description: 'Feature inquiry' },

  // General queries
  { query: 'Who will win the Bundesliga?', expected: 'general', description: 'Prediction requiring all data' },
  { query: 'Give me an overview of Bundesliga', expected: 'general', description: 'General overview' },
];

console.log('\n🧪 Query Classifier - Week 1 Keyword Baseline Test\n');
console.log('='.repeat(80));

const results = testCases.map(({ query, expected, description }) => {
  const result = classifyQuery(query);
  const correct = result.category === expected;

  return {
    query,
    expected,
    actual: result.category,
    confidence: result.confidence,
    correct,
    description,
    matchedPatterns: result.matchedPatterns,
  };
});

// Print results
results.forEach((r, idx) => {
  const status = r.correct ? '✅' : '❌';
  console.log(`\n${idx + 1}. ${status} ${r.description}`);
  console.log(`   Query: "${r.query}"`);
  console.log(`   Expected: ${r.expected} | Actual: ${r.actual} | Confidence: ${(r.confidence * 100).toFixed(0)}%`);
  if (r.matchedPatterns && r.matchedPatterns.length > 0) {
    console.log(`   Matched: ${r.matchedPatterns.slice(0, 2).join(', ')}`);
  }
});

// Calculate accuracy
const correctCount = results.filter(r => r.correct).length;
const accuracy = (correctCount / results.length) * 100;

console.log('\n' + '='.repeat(80));
console.log(`\n📈 Accuracy: ${accuracy.toFixed(1)}% (${correctCount}/${results.length})`);
console.log(`🎯 Target: 75%+ (Week 1 baseline)`);
console.log(`Status: ${accuracy >= 75 ? '✅ PASSED - Ready for Week 2' : '⚠️ NEEDS IMPROVEMENT'}\n`);

// Token savings analysis
console.log('💰 Token Savings Estimates\n');
console.log('='.repeat(80));
const categories: QueryCategory[] = ['news', 'player', 'match', 'standings', 'meta', 'general'];
categories.forEach(cat => {
  const result = estimateTokenSavings(cat as QueryCategory);
  const sources = getRequiredDataSources(cat);
  console.log(
    `${cat.padEnd(12)}: ${result.optimizedTokens.toLocaleString().padStart(8)} tokens ` +
    `(${result.savingsPercent.toString().padStart(2)}% savings) - ${sources.length} data sources`
  );
});
console.log('='.repeat(80) + '\n');

// Performance test
console.log('⚡ Performance Benchmark\n');
console.log('='.repeat(80));
const perfQuery = "When does Bayern play next?";
const iterations = 1000;

const start = performance.now();
for (let i = 0; i < iterations; i++) {
  classifyQuery(perfQuery);
}
const end = performance.now();

const avgTime = (end - start) / iterations;
console.log(`Average classification time: ${avgTime.toFixed(3)}ms (${iterations} iterations)`);
console.log(`Target: < 5ms per classification`);
console.log(`Status: ${avgTime < 5 ? '✅ PASSED' : '⚠️ SLOW'}\n`);
console.log('='.repeat(80) + '\n');

// Exit with error code if accuracy below target
process.exit(accuracy >= 75 ? 0 : 1);
