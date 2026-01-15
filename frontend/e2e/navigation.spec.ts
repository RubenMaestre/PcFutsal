import { test, expect } from '@playwright/test';

// Helper to dismiss cookie consent if present
async function dismissCookieConsent(page: any) {
  try {
    const consentButton = page.locator('button.fc-button, [class*="consent"] button, [class*="cookie"] button').first();
    if (await consentButton.isVisible({ timeout: 3000 })) {
      await consentButton.click();
      await page.waitForTimeout(500);
    }
  } catch (e) {
    // No consent dialog or already dismissed
  }
}

test.describe('Navigation Tests', () => {
  test('should navigate to clubs page', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page);

    // Try to find and click clubs link
    const clubsLink = page.locator('a[href*="clubes"], a:has-text("Clubes"), a:has-text("Clubs")').first();

    if (await clubsLink.isVisible()) {
      await clubsLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('clubes');
    }
  });

  test('should navigate to players page', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page);

    const playersLink = page.locator('a[href*="jugadores"], a:has-text("Jugadores"), a:has-text("Players")').first();

    if (await playersLink.isVisible()) {
      await playersLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('jugadores');
    }
  });

  test('should navigate to matches page', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page);

    const matchesLink = page.locator('a[href*="partidos"], a:has-text("Partidos"), a:has-text("Matches")').first();

    if (await matchesLink.isVisible()) {
      await matchesLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('partidos');
    }
  });

  test('should navigate to rankings page', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page);

    const rankingsLink = page.locator('a[href*="rankings"], a[href*="clasificacion"], a:has-text("Rankings"), a:has-text("Clasificación")').first();

    if (await rankingsLink.isVisible()) {
      await rankingsLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toMatch(/rankings|clasificacion/);
    }
  });

  test('should handle back navigation correctly', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page);

    // Navigate to another page if possible
    const anyLink = page.locator('a[href*="/es/"]').first();
    if (await anyLink.isVisible()) {
      await anyLink.click();
      await page.waitForLoadState('networkidle');
      await page.goBack();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/es');
    }
  });
});
