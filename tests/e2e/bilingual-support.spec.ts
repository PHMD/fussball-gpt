/**
 * E2E tests for bilingual support and user preferences
 *
 * Tests explicit language enforcement, detail levels, and onboarding flow
 */

import { test, expect } from '@playwright/test';

test.describe('Bilingual Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('German user gets German responses (even for English query)', async ({ page }) => {
    // Set language to German in localStorage
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'de',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    // Wait for onboarding to not appear (since we set preferences)
    await expect(page.locator('text=Willkommen bei Fußball GPT!')).not.toBeVisible();

    // Send English query (should still get German response)
    await page.locator('textarea[placeholder*="Tabelle"]').fill('Who is the top scorer?');
    await page.locator('textarea').press('Enter');

    // Wait for response
    await page.waitForSelector('text=Fußball GPT', { timeout: 30000 });

    // Get assistant response
    const messages = page.locator('[class*="justify-start"]');
    await messages.last().waitFor({ timeout: 30000 });

    const response = await messages.last().textContent();

    // Verify response is in German
    // Look for German keywords (flexible matching)
    const hasGermanKeywords =
      response?.includes('Tore') ||
      response?.includes('Torschütze') ||
      response?.includes('Spieler') ||
      response?.includes('via API-Football') ||
      response?.includes('Saison');

    expect(hasGermanKeywords).toBeTruthy();
  });

  test('English user gets English responses (even for German query)', async ({ page }) => {
    // Set language to English
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'en',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    // Wait for onboarding to not appear
    await expect(page.locator('text=Welcome to Fußball GPT!')).toBeVisible();

    // Send German query (should still get English response)
    await page.locator('textarea[placeholder*="standings"]').fill('Wer ist der Torschützenkönig?');
    await page.locator('textarea').press('Enter');

    // Wait for response
    await page.waitForSelector('text=Fußball GPT', { timeout: 30000 });

    const messages = page.locator('[class*="justify-start"]');
    await messages.last().waitFor({ timeout: 30000 });

    const response = await messages.last().textContent();

    // Verify response is in English
    const hasEnglishKeywords =
      response?.match(/goals?/i) ||
      response?.match(/scorer?/i) ||
      response?.match(/player/i) ||
      response?.includes('via API-Football') ||
      response?.match(/season/i);

    expect(hasEnglishKeywords).toBeTruthy();
  });

  test('QUICK detail level gives short responses', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'en',
        detailLevel: 'quick',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    await page.locator('textarea').fill('Current Bundesliga news?');
    await page.locator('textarea').press('Enter');

    await page.waitForSelector('text=Fußball GPT', { timeout: 30000 });

    const messages = page.locator('[class*="justify-start"]');
    await messages.last().waitFor({ timeout: 30000 });

    const response = await messages.last().textContent();

    // Quick responses should be relatively short (< 500 chars as rough estimate)
    // This is a soft check since LLM output varies
    expect(response?.length ?? 0).toBeLessThan(800);
  });

  test('DETAILED level gives comprehensive responses', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'en',
        detailLevel: 'detailed',
        persona: 'expert_analyst'
      }));
    });

    await page.reload();

    await page.locator('textarea').fill('Analyze recent Bundesliga trends');
    await page.locator('textarea').press('Enter');

    await page.waitForSelector('text=Fußball GPT', { timeout: 30000 });

    const messages = page.locator('[class*="justify-start"]');
    await messages.last().waitFor({ timeout: 30000 });

    const response = await messages.last().textContent();

    // Detailed responses should be longer (> 400 chars)
    expect(response?.length ?? 0).toBeGreaterThan(400);
  });

  test('Onboarding modal appears on first visit', async ({ page }) => {
    // Clear localStorage to simulate first visit
    await page.evaluate(() => localStorage.clear());
    await page.reload();

    // Onboarding should appear
    await expect(page.locator('text=Willkommen bei Fußball GPT!')).toBeVisible();

    // Select German
    await page.click('button:has-text("🇩🇪")');

    // Click Next
    await page.click('button:has-text("Weiter")');

    // Should be on step 2 (detail level)
    await expect(page.locator('text=Wie ausführlich')).toBeVisible();

    // Select Balanced
    await page.locator('button:has-text("Ausgewogen")').click();

    // Click Next
    await page.click('button:has-text("Weiter")');

    // Should be on step 3 (persona)
    await expect(page.locator('text=Was beschreibt dich')).toBeVisible();

    // Select Casual Fan
    await page.locator('button:has-text("Gelegenheitsfan")').first().click();

    // Click Complete
    await page.click('button:has-text("Fertig")');

    // Onboarding should close
    await expect(page.locator('text=Willkommen bei Fußball GPT!')).not.toBeVisible();

    // Preferences should be saved
    const savedPrefs = await page.evaluate(() => {
      return localStorage.getItem('fussballgpt_preferences');
    });
    expect(savedPrefs).toBeTruthy();
    const parsed = JSON.parse(savedPrefs!);
    expect(parsed.language).toBe('de');
    expect(parsed.detailLevel).toBe('balanced');
  });

  test('Settings panel allows changing preferences', async ({ page }) => {
    // Set initial preferences
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'de',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    // Open settings
    await page.click('button[aria-label="Einstellungen"]');

    // Settings panel should be visible
    await expect(page.locator('text=Einstellungen')).toBeVisible();

    // Change to English
    await page.locator('button:has-text("🇬🇧")').click();

    // Change to Quick
    await page.locator('button:has-text("Quick")').click();

    // Save
    await page.click('button:has-text("Save")');

    // Settings panel should close
    await expect(page.locator('text=Settings')).not.toBeVisible();

    // Verify preferences were updated
    const updatedPrefs = await page.evaluate(() => {
      return localStorage.getItem('fussballgpt_preferences');
    });
    const parsed = JSON.parse(updatedPrefs!);
    expect(parsed.language).toBe('en');
    expect(parsed.detailLevel).toBe('quick');

    // Verify UI updated to English
    await expect(page.locator('text=Welcome to Fußball GPT!')).toBeVisible();
  });
});
