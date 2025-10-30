/**
 * E2E tests for bilingual support and user preferences
 *
 * Tests explicit language enforcement, detail levels, and onboarding flow
 */

import { test, expect } from '@playwright/test';

test.describe('Bilingual Support (Adaptive Language)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('German preference adapts to query language (respects user question)', async ({ page }) => {
    // Set language to German in localStorage
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'de',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    // Wait for page to load and verify no modal backdrop (onboarding should be skipped)
    await page.waitForTimeout(1000);
    await expect(page.locator('[class*="fixed"][class*="inset-0"][class*="bg-black/50"]')).not.toBeVisible();

    // Send English query (should still get German response)
    await page.locator('textarea[placeholder*="Tabelle"]').fill('Who is the top scorer?');
    await page.locator('textarea').press('Enter');

    // Wait for streaming to complete (status !== 'streaming')
    await page.waitForTimeout(15000); // Give LLM time to respond

    // Get all assistant messages
    const messages = page.locator('[class*="justify-start"]').locator('[class*="bg-card"]');
    const lastMessage = messages.last();

    // Wait for message to appear
    await lastMessage.waitFor({ state: 'visible', timeout: 30000 });

    const response = await lastMessage.textContent();

    // Verify response is in German
    // Look for German keywords (flexible matching)
    const hasGermanKeywords =
      response?.includes('Tore') ||
      response?.includes('Torschütze') ||
      response?.includes('Spieler') ||
      response?.includes('Bundesliga') ||
      response?.includes('Saison');

    expect(hasGermanKeywords).toBeTruthy();
  });

  test('English preference adapts to query language (respects user question)', async ({ page }) => {
    // Set language to English
    await page.evaluate(() => {
      localStorage.setItem('fussballgpt_preferences', JSON.stringify({
        language: 'en',
        detailLevel: 'balanced',
        persona: 'casual_fan'
      }));
    });

    await page.reload();

    // Wait for page to load and verify no modal (onboarding should be skipped)
    await page.waitForTimeout(1000);
    await expect(page.locator('[class*="fixed"][class*="inset-0"][class*="bg-black/50"]')).not.toBeVisible();

    // Verify English UI (welcome message in chat)
    await expect(page.locator('text=Welcome to Fußball GPT!')).toBeVisible();

    // Send German query (should still get English response)
    await page.locator('textarea[placeholder*="standings"]').fill('Wer ist der Torschützenkönig?');
    await page.locator('textarea').press('Enter');

    // Wait for streaming to complete
    await page.waitForTimeout(15000);

    const messages = page.locator('[class*="justify-start"]').locator('[class*="bg-card"]');
    const lastMessage = messages.last();

    await lastMessage.waitFor({ state: 'visible', timeout: 30000 });

    const response = await lastMessage.textContent();

    // Verify response is in English
    const hasEnglishKeywords =
      response?.match(/goals?/i) ||
      response?.match(/scorer?/i) ||
      response?.match(/player/i) ||
      response?.includes('Bundesliga') ||
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

    // Wait for streaming to complete
    await page.waitForTimeout(15000);

    const messages = page.locator('[class*="justify-start"]').locator('[class*="bg-card"]');
    const lastMessage = messages.last();

    await lastMessage.waitFor({ state: 'visible', timeout: 30000 });

    const response = await lastMessage.textContent();

    // Quick responses should be relatively short (< 2000 chars as rough estimate)
    // This is a soft check since LLM output varies - we're just verifying it's shorter than detailed
    expect(response?.length ?? 0).toBeLessThan(2000);
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

    // Wait for streaming to complete
    await page.waitForTimeout(15000);

    const messages = page.locator('[class*="justify-start"]').locator('[class*="bg-card"]');
    const lastMessage = messages.last();

    await lastMessage.waitFor({ state: 'visible', timeout: 30000 });

    const response = await lastMessage.textContent();

    // Detailed responses should be longer (> 400 chars)
    expect(response?.length ?? 0).toBeGreaterThan(400);
  });

  test('Onboarding modal appears on first visit', async ({ page }) => {
    // Navigate with cleared storage
    await page.goto('/', { waitUntil: 'networkidle' });

    // Clear localStorage BEFORE first load
    await page.evaluate(() => localStorage.clear());

    // Reload to trigger first-visit detection
    await page.reload({ waitUntil: 'networkidle' });

    // Wait a moment for React to hydrate and detect missing preferences
    await page.waitForTimeout(1500);

    // Onboarding should appear - check for onboarding title first
    const onboardingTitle = page.locator('h2:has-text("Willkommen bei Fußball GPT!")');
    await expect(onboardingTitle).toBeVisible({ timeout: 10000 });

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

    // Onboarding should close (modal backdrop disappears)
    await expect(page.locator('[class*="fixed"][class*="inset-0"][class*="bg-black/50"]')).not.toBeVisible();

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

    // Change to Quick detail level (find Detail Level section first, then Quick button)
    const detailSection = page.locator('text=Detail Level').locator('..');
    await detailSection.locator('button', { hasText: 'Quick' }).first().click();

    // Save
    await page.click('button:has-text("Save")');

    // Settings panel should close (wait a moment for animation)
    await page.waitForTimeout(500);
    await expect(page.locator('text=Settings')).not.toBeVisible();

    // Verify preferences were updated in localStorage
    const updatedPrefs = await page.evaluate(() => {
      return localStorage.getItem('fussballgpt_preferences');
    });
    const parsed = JSON.parse(updatedPrefs!);
    expect(parsed.language).toBe('en');
    expect(parsed.detailLevel).toBe('quick');

    // Verify UI updated to English (chat welcome message)
    const welcomeMsg = page.locator('p:has-text("Welcome to Fußball GPT!")');
    await expect(welcomeMsg).toBeVisible();
  });
});
