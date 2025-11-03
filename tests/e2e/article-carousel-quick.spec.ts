/**
 * Quick E2E test for PHM-61 Article Carousel
 *
 * Tests: Does carousel appear and what's the timing?
 */

import { test, expect } from '@playwright/test';

test.describe('Article Carousel Quick Test', () => {
  test('Verify carousel appears and capture timing', async ({ page }) => {
    // Set preferences to skip onboarding
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'en',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });
    await page.reload();
    await page.waitForLoadState('domcontentloaded');

    // Track timing
    const events: string[] = [];
    const startTime = Date.now();
    const log = (msg: string) => {
      const elapsed = Date.now() - startTime;
      events.push(`[${elapsed}ms] ${msg}`);
      console.log(`[${elapsed}ms] ${msg}`);
    };

    log('Page loaded');

    // Submit query
    const textarea = page.locator('textarea');
    await textarea.fill('Bayern Munich latest news');
    log('Query entered');

    await textarea.press('Enter');
    log('Query submitted');

    // Race condition: which appears first?
    const carouselPromise = page.locator('h3:has-text("Recent Articles")').waitFor({
      state: 'visible',
      timeout: 30000
    }).then(() => {
      log('✅ CAROUSEL HEADING VISIBLE');
      return 'carousel';
    }).catch(() => {
      log('❌ Carousel heading timeout');
      return 'carousel-timeout';
    });

    const responsePromise = page.locator('.prose').first().waitFor({
      state: 'visible',
      timeout: 30000
    }).then(() => {
      log('✅ AI RESPONSE TEXT VISIBLE');
      return 'response';
    }).catch(() => {
      log('❌ Response text timeout');
      return 'response-timeout';
    });

    // Wait for BOTH
    const [carouselResult, responseResult] = await Promise.all([
      carouselPromise,
      responsePromise
    ]);

    log(`Carousel result: ${carouselResult}`);
    log(`Response result: ${responseResult}`);

    // Take screenshot
    await page.screenshot({ path: 'carousel-test-screenshot.png', fullPage: true });
    log('Screenshot saved');

    // Verify carousel appeared
    expect(carouselResult).toBe('carousel');

    // Count articles
    const cards = page.locator('[id^="citation-"]');
    const count = await cards.count();
    log(`Found ${count} article cards`);

    // Check first card details
    if (count > 0) {
      const firstCard = cards.first();
      const title = await firstCard.locator('[class*="text-sm"]').first().textContent();
      log(`First card title: ${title?.substring(0, 50)}...`);

      // Check for summary
      const summaries = await firstCard.locator('p.text-xs.text-muted-foreground.line-clamp-3').count();
      log(`First card has summary: ${summaries > 0}`);
    }

    // Print summary
    console.log('\n=== TEST SUMMARY ===');
    events.forEach(e => console.log(e));
    console.log('====================\n');

    // Assertions
    expect(count).toBeGreaterThan(0);
  });
});
