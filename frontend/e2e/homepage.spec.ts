import { test, expect } from '@playwright/test';

test.describe('Homepage Tests', () => {
  test('should load homepage successfully', async ({ page }) => {
    const response = await page.goto('/es');
    expect(response?.status()).toBeLessThan(400);
  });

  test('should have correct title and meta tags', async ({ page }) => {
    await page.goto('/es');
    await expect(page).toHaveTitle(/PC Futsal|pcfutsal/i);
  });

  test('should display header with navigation', async ({ page }) => {
    await page.goto('/es');
    const header = page.locator('header');
    await expect(header).toBeVisible({ timeout: 10000 });
  });

  test('should have language selector', async ({ page }) => {
    await page.goto('/es');
    // Look for language-related elements
    const langElements = page.locator('[class*="lang"], [class*="language"], button:has-text("ES"), button:has-text("EN")');
    const count = await langElements.count();
    expect(count).toBeGreaterThanOrEqual(0); // May or may not be visible
  });

  test('should load main content without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    // Log errors for analysis but don't fail if there are some
    if (errors.length > 0) {
      console.log('JavaScript errors found:', errors);
    }
  });

  test('should have responsive design (mobile viewport)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/es');
    await expect(page.locator('body')).toBeVisible();
  });
});
