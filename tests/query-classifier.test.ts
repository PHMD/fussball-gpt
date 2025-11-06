/**
 * Query Classifier Tests - Week 1: Keyword Baseline
 *
 * Testing with 20 example queries from research
 * Target: 75%+ accuracy (15/20 correct)
 */

import { describe, it, expect } from '@jest/globals';
import { classifyQuery, getRequiredDataSources, estimateTokenSavings } from '../lib/query-classifier';
import type { QueryCategory } from '../lib/query-classifier';

describe('Query Classifier - Keyword Baseline', () => {
  // Test cases from Linear issue description
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

  it('should correctly classify all test queries', () => {
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

    // Calculate accuracy
    const correctCount = results.filter(r => r.correct).length;
    const accuracy = (correctCount / results.length) * 100;

    // Log detailed results
    console.log('\n📊 Query Classification Test Results\n');
    console.log('=' .repeat(80));

    results.forEach((r, idx) => {
      const status = r.correct ? '✅' : '❌';
      console.log(`\n${idx + 1}. ${status} ${r.description}`);
      console.log(`   Query: "${r.query}"`);
      console.log(`   Expected: ${r.expected} | Actual: ${r.actual} | Confidence: ${r.confidence}`);
      if (r.matchedPatterns && r.matchedPatterns.length > 0) {
        console.log(`   Matched: ${r.matchedPatterns.slice(0, 2).join(', ')}`);
      }
    });

    console.log('\n' + '='.repeat(80));
    console.log(`\n📈 Accuracy: ${accuracy.toFixed(1)}% (${correctCount}/${results.length})`);
    console.log(`🎯 Target: 75%+ (Week 1 baseline)`);
    console.log(`Status: ${accuracy >= 75 ? '✅ PASSED' : '⚠️ NEEDS IMPROVEMENT'}\n`);

    // Week 1 target: 75% accuracy
    expect(accuracy).toBeGreaterThanOrEqual(75);
  });

  it('should return required data sources for each category', () => {
    const categories: QueryCategory[] = ['news', 'player', 'match', 'standings', 'meta', 'general'];

    categories.forEach(category => {
      const sources = getRequiredDataSources(category);

      // Meta should have no data sources
      if (category === 'meta') {
        expect(sources).toHaveLength(0);
      }
      // General should have all data sources
      else if (category === 'general') {
        expect(sources.length).toBeGreaterThan(4);
      }
      // Specific categories should have limited sources
      else {
        expect(sources.length).toBeGreaterThan(0);
        expect(sources.length).toBeLessThan(6);
      }
    });
  });

  it('should estimate token savings correctly', () => {
    // Test token savings for specific categories
    const newsResult = estimateTokenSavings('news');
    expect(newsResult.savingsPercent).toBeGreaterThan(85); // Should save >85%

    const metaResult = estimateTokenSavings('meta');
    expect(metaResult.savingsPercent).toBeGreaterThan(95); // Should save >95%

    const generalResult = estimateTokenSavings('general');
    expect(generalResult.savingsPercent).toBe(0); // No savings for general

    console.log('\n💰 Token Savings Estimates\n');
    console.log('='.repeat(50));
    ['news', 'player', 'match', 'standings', 'meta', 'general'].forEach(cat => {
      const result = estimateTokenSavings(cat as QueryCategory);
      console.log(`${cat.padEnd(12)}: ${result.optimizedTokens.toLocaleString().padStart(8)} tokens (${result.savingsPercent}% savings)`);
    });
    console.log('='.repeat(50) + '\n');
  });

  it('should have high confidence for regex matches', () => {
    const result = classifyQuery("When does Bayern play next?");
    expect(result.confidence).toBeGreaterThanOrEqual(0.8);
    expect(result.method).toBe('keyword');
  });

  it('should fallback to general for unclear queries', () => {
    const ambiguousQueries = [
      'Tell me something',
      'Bundesliga',
      'What do you think?',
    ];

    ambiguousQueries.forEach(query => {
      const result = classifyQuery(query);
      expect(['general', 'news']).toContain(result.category);
      expect(result.confidence).toBeLessThanOrEqual(0.7);
    });
  });

  it('should handle case insensitivity', () => {
    const variants = [
      'WHEN DOES BAYERN PLAY?',
      'when does bayern play?',
      'When Does Bayern Play?',
    ];

    variants.forEach(query => {
      const result = classifyQuery(query);
      expect(result.category).toBe('match');
    });
  });

  it('should handle whitespace variations', () => {
    const variants = [
      '  Show me the table  ',
      'Show me the table',
      '   Show   me   the   table   ',
    ];

    variants.forEach(query => {
      const result = classifyQuery(query);
      expect(result.category).toBe('standings');
    });
  });
});

describe('Query Classifier - Performance Benchmarks', () => {
  it('should classify queries quickly (< 5ms)', () => {
    const query = "When does Bayern play next?";
    const iterations = 1000;

    const start = performance.now();
    for (let i = 0; i < iterations; i++) {
      classifyQuery(query);
    }
    const end = performance.now();

    const avgTime = (end - start) / iterations;

    console.log(`\n⚡ Performance: ${avgTime.toFixed(3)}ms per classification (${iterations} iterations)\n`);

    // Should be very fast (< 5ms per classification)
    expect(avgTime).toBeLessThan(5);
  });
});
