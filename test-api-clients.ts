/**
 * Test script for API clients
 *
 * Run with: npx tsx test-api-clients.ts
 */

import { fetchKickerRss } from './lib/api-clients/kicker-rss';

async function testKickerRss() {
  console.log('\n🧪 Testing Kicker RSS client...\n');

  try {
    const articles = await fetchKickerRss();

    console.log(`✅ Fetched ${articles.length} Bundesliga articles from Kicker RSS\n`);

    if (articles.length > 0) {
      console.log('📰 Sample article:');
      const article = articles[0];
      console.log(`  Title: ${article.title}`);
      console.log(`  Source: ${article.source}`);
      console.log(`  URL: ${article.url}`);
      console.log(`  Timestamp: ${article.timestamp.toISOString()}`);
      console.log(`  Content preview: ${article.content.substring(0, 100)}...`);
    } else {
      console.log('⚠️  No Bundesliga articles found (might need to adjust filters)');
    }
  } catch (error) {
    console.error('❌ Error testing Kicker RSS:', error);
  }
}

async function main() {
  console.log('=== API Client Tests ===');

  await testKickerRss();

  console.log('\n✅ All tests complete!\n');
}

main().catch(console.error);
