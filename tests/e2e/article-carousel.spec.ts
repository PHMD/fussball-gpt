/**
 * E2E tests for PHM-61 Article Carousel implementation
 *
 * Tests timing, visibility, and structure of article carousel that appears
 * BEFORE AI response streaming begins.
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Article Carousel (PHM-61)', () => {
  test.beforeEach(async ({ page }) => {
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
    await page.waitForTimeout(1000);
  });

  test('Carousel appears BEFORE AI response starts streaming', async ({ page }) => {
    const timingLog: Array<{ timestamp: number; event: string }> = [];
    const startTime = Date.now();

    // Log function
    const log = (event: string) => {
      timingLog.push({ timestamp: Date.now() - startTime, event });
    };

    // Set up observers BEFORE submitting query
    const carouselPromise = page.waitForSelector('h3:has-text("Recent Articles")', {
      timeout: 30000
    }).then(() => {
      log('Carousel heading appeared');
    });

    const responsePromise = page.waitForSelector('.prose', {
      timeout: 30000
    }).then(() => {
      log('AI response text appeared');
    });

    // Submit query
    await page.locator('textarea').fill('Bayern Munich latest news');
    await page.locator('textarea').press('Enter');
    log('Query submitted');

    // Wait for both to appear
    await Promise.all([carouselPromise, responsePromise]);

    // Print timing log for debugging
    console.log('Timing Log:');
    timingLog.forEach(entry => {
      console.log(`  ${entry.timestamp}ms: ${entry.event}`);
    });

    // Find when each appeared
    const carouselTime = timingLog.find(e => e.event === 'Carousel heading appeared')?.timestamp ?? Infinity;
    const responseTime = timingLog.find(e => e.event === 'AI response text appeared')?.timestamp ?? Infinity;

    // ASSERTION: Carousel must appear before or at same time as response
    expect(carouselTime).toBeLessThanOrEqual(responseTime);

    console.log(`\nResult: Carousel appeared ${carouselTime}ms after query, Response appeared ${responseTime}ms after query`);
    console.log(`Carousel was ${responseTime - carouselTime}ms faster than response`);
  });

  test('Carousel structure validation', async ({ page }) => {
    // Submit query
    await page.locator('textarea').fill('Bundesliga news');
    await page.locator('textarea').press('Enter');

    // Wait for carousel
    const carouselHeading = page.locator('h3:has-text("Recent Articles")');
    await carouselHeading.waitFor({ state: 'visible', timeout: 30000 });

    // Take screenshot when carousel appears
    await page.screenshot({ path: 'test-results/carousel-appeared.png', fullPage: true });

    // Check carousel structure
    const carousel = page.locator('[class*="carousel"]').first();
    await expect(carousel).toBeVisible();

    // Check for article cards
    const cards = page.locator('[id^="citation-"]');
    const cardCount = await cards.count();

    console.log(`\nFound ${cardCount} article cards`);

    // Verify at least some articles exist
    expect(cardCount).toBeGreaterThan(0);

    // Check first card structure
    const firstCard = cards.first();

    // Should have an image (or empty div if failed to load)
    const hasImage = await firstCard.locator('img').count() > 0;
    console.log(`First card has image: ${hasImage}`);

    // Should have domain/source
    const domainElement = firstCard.locator('.text-xs.text-muted-foreground').first();
    const domain = await domainElement.textContent();
    console.log(`First card domain: ${domain}`);

    // Should have title
    const titleElement = firstCard.locator('[class*="text-sm"]').first();
    const title = await titleElement.textContent();
    console.log(`First card title: ${title}`);

    // Check if cards have summaries
    const summaryElements = firstCard.locator('p.text-xs.text-muted-foreground.line-clamp-3');
    const hasSummary = await summaryElements.count() > 0;
    console.log(`First card has summary: ${hasSummary}`);

    if (hasSummary) {
      const summary = await summaryElements.first().textContent();
      console.log(`First card summary preview: ${summary?.substring(0, 100)}...`);
    }
  });

  test('Carousel timing analysis (detailed)', async ({ page }) => {
    const events: Array<{ timestamp: number; event: string; details?: string }> = [];
    const startTime = Date.now();

    const log = (event: string, details?: string) => {
      events.push({ timestamp: Date.now() - startTime, event, details });
    };

    // Monitor DOM mutations
    await page.evaluate(() => {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node instanceof HTMLElement) {
              // Log when carousel elements appear
              if (node.textContent?.includes('Recent Articles') ||
                  node.textContent?.includes('Aktuelle Artikel')) {
                (window as any).__carouselHeadingTime = Date.now();
              }
              // Log when citation cards appear
              if (node.id?.startsWith('citation-')) {
                (window as any).__firstCardTime = (window as any).__firstCardTime || Date.now();
              }
              // Log when prose/response appears
              if (node.classList?.contains('prose')) {
                (window as any).__responseTime = Date.now();
              }
            }
          });
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    });

    // Submit query
    await page.locator('textarea').fill('Latest Bundesliga results');
    log('Query submitted');
    await page.locator('textarea').press('Enter');

    // Wait for response to complete
    await page.waitForTimeout(20000);

    // Extract timing data from browser
    const browserTimings = await page.evaluate(() => {
      return {
        carouselHeading: (window as any).__carouselHeadingTime,
        firstCard: (window as any).__firstCardTime,
        response: (window as any).__responseTime,
      };
    });

    // Log browser timings
    if (browserTimings.carouselHeading) {
      log('Carousel heading detected in DOM', `at ${browserTimings.carouselHeading}ms`);
    }
    if (browserTimings.firstCard) {
      log('First card detected in DOM', `at ${browserTimings.firstCard}ms`);
    }
    if (browserTimings.response) {
      log('Response text detected in DOM', `at ${browserTimings.response}ms`);
    }

    // Take final screenshot
    await page.screenshot({ path: 'test-results/carousel-final-state.png', fullPage: true });

    // Print detailed report
    console.log('\n=== TIMING REPORT ===');
    events.forEach(e => {
      const details = e.details ? ` (${e.details})` : '';
      console.log(`${e.timestamp}ms: ${e.event}${details}`);
    });
    console.log('====================\n');

    // Verify carousel appeared
    const carouselHeading = page.locator('h3:has-text("Recent Articles")');
    await expect(carouselHeading).toBeVisible();
  });

  test('German language carousel heading', async ({ page }) => {
    // Set German language
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'de',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });
    await page.reload();
    await page.waitForTimeout(1000);

    // Submit query
    await page.locator('textarea').fill('Bayern München Nachrichten');
    await page.locator('textarea').press('Enter');

    // Wait for German carousel heading
    const germanHeading = page.locator('h3:has-text("Aktuelle Artikel")');
    await germanHeading.waitFor({ state: 'visible', timeout: 30000 });

    // Verify it's visible
    await expect(germanHeading).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/carousel-german.png', fullPage: true });
  });

  test('Carousel only shows on last assistant message', async ({ page }) => {
    // First query
    await page.locator('textarea').fill('Bayern news');
    await page.locator('textarea').press('Enter');

    // Wait for first response
    await page.waitForTimeout(15000);

    // Count carousels (should be 1)
    let carouselCount = await page.locator('h3:has-text("Recent Articles")').count();
    console.log(`After first query: ${carouselCount} carousel(s)`);
    expect(carouselCount).toBe(1);

    // Second query
    await page.locator('textarea').fill('Current standings');
    await page.locator('textarea').press('Enter');

    // Wait for second response
    await page.waitForTimeout(15000);

    // Count carousels (should still be 1 - only on last message)
    carouselCount = await page.locator('h3:has-text("Recent Articles")').count();
    console.log(`After second query: ${carouselCount} carousel(s)`);
    expect(carouselCount).toBe(1);

    // Take screenshot
    await page.screenshot({ path: 'test-results/carousel-multiple-messages.png', fullPage: true });
  });
});
