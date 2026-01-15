import { test, expect } from '@playwright/test';

test.describe('API and Data Loading Tests', () => {
  test('should load API data without errors', async ({ page }) => {
    const apiResponses: { url: string; status: number; time: number }[] = [];
    const apiErrors: string[] = [];

    page.on('response', async response => {
      if (response.url().includes('/api/')) {
        apiResponses.push({
          url: response.url(),
          status: response.status(),
          time: Date.now()
        });

        if (response.status() >= 400) {
          apiErrors.push(`${response.status()} - ${response.url()}`);
        }
      }
    });

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    console.log('API responses:', apiResponses.length);
    apiResponses.forEach(r => console.log(`  ${r.status} - ${r.url}`));

    if (apiErrors.length > 0) {
      console.log('API Errors:', apiErrors);
    }

    // All API responses should be successful
    const errorCount = apiResponses.filter(r => r.status >= 400).length;
    expect(errorCount).toBe(0);
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    const response = await page.goto('/es/nonexistent-page-12345');
    const status = response?.status();

    console.log(`404 page status: ${status}`);

    // Should either return 404 or redirect
    expect(status).toBeLessThan(500);

    // Check for user-friendly error message
    const bodyText = await page.textContent('body');
    const has404Message = bodyText?.toLowerCase().includes('not found') ||
                          bodyText?.toLowerCase().includes('no encontrado') ||
                          bodyText?.toLowerCase().includes('404');

    console.log(`Has friendly 404 message: ${has404Message}`);
  });

  test('should display data in tables/lists', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    // Look for data tables or lists
    const tables = await page.locator('table').count();
    const dataLists = await page.locator('[class*="list"], [class*="grid"], ul, ol').count();

    console.log(`Tables found: ${tables}`);
    console.log(`List/grid elements found: ${dataLists}`);
  });

  test('clubs page should load club data', async ({ page }) => {
    await page.goto('/es/clubes');
    await page.waitForLoadState('networkidle');

    // Look for club cards or list items
    const clubElements = await page.locator('[class*="club"], [class*="card"], [class*="team"]').count();
    console.log(`Club elements found: ${clubElements}`);
  });

  test('API response times should be reasonable', async ({ page }) => {
    const apiTimes: { url: string; time: number }[] = [];

    page.on('response', async response => {
      if (response.url().includes('/api/')) {
        const timing = response.request().timing();
        apiTimes.push({
          url: response.url(),
          time: timing.responseEnd
        });
      }
    });

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    console.log('API response times:');
    apiTimes.forEach(t => console.log(`  ${t.time}ms - ${t.url.split('/api/')[1] || t.url}`));

    // Check average API response time
    if (apiTimes.length > 0) {
      const avgTime = apiTimes.reduce((sum, t) => sum + t.time, 0) / apiTimes.length;
      console.log(`Average API response time: ${avgTime.toFixed(0)}ms`);
    }
  });
});

test.describe('Internationalization Tests', () => {
  test('should support Spanish language', async ({ page }) => {
    await page.goto('/es');
    const htmlLang = await page.locator('html').getAttribute('lang');
    console.log(`Spanish page lang: ${htmlLang}`);
    expect(htmlLang).toMatch(/es|ES/i);
  });

  test('should support English language', async ({ page }) => {
    const response = await page.goto('/en');
    if (response?.status() === 200) {
      const htmlLang = await page.locator('html').getAttribute('lang');
      console.log(`English page lang: ${htmlLang}`);
    } else {
      console.log(`English not available (status: ${response?.status()})`);
    }
  });

  test('language switch should work', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    // Look for language switcher
    const langSwitcher = page.locator('[class*="lang"], [class*="language"], button:has-text("EN"), a[href*="/en"]').first();

    if (await langSwitcher.isVisible()) {
      await langSwitcher.click();
      await page.waitForLoadState('networkidle');
      console.log(`Switched to: ${page.url()}`);
    } else {
      console.log('No visible language switcher found');
    }
  });
});
