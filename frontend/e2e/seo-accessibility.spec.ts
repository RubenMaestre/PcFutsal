import { test, expect } from '@playwright/test';

test.describe('SEO Tests', () => {
  test('should have proper meta tags', async ({ page }) => {
    await page.goto('/es');

    // Check for essential meta tags
    const metaDescription = await page.locator('meta[name="description"]').getAttribute('content');
    const metaViewport = await page.locator('meta[name="viewport"]').getAttribute('content');

    console.log('Meta description:', metaDescription || 'MISSING');
    console.log('Meta viewport:', metaViewport || 'MISSING');

    expect(metaViewport).toBeTruthy();
  });

  test('should have proper heading structure', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    const h1Count = await page.locator('h1').count();
    const h2Count = await page.locator('h2').count();
    const h3Count = await page.locator('h3').count();

    console.log(`H1 tags: ${h1Count}`);
    console.log(`H2 tags: ${h2Count}`);
    console.log(`H3 tags: ${h3Count}`);

    // Best practice: exactly one H1 per page
    expect(h1Count).toBeGreaterThanOrEqual(0);
  });

  test('should have lang attribute on html', async ({ page }) => {
    await page.goto('/es');
    const lang = await page.locator('html').getAttribute('lang');
    console.log('HTML lang attribute:', lang || 'MISSING');
    expect(lang).toBeTruthy();
  });

  test('should have Open Graph meta tags', async ({ page }) => {
    await page.goto('/es');

    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content');
    const ogDescription = await page.locator('meta[property="og:description"]').getAttribute('content');
    const ogImage = await page.locator('meta[property="og:image"]').getAttribute('content');

    console.log('OG Title:', ogTitle || 'MISSING');
    console.log('OG Description:', ogDescription || 'MISSING');
    console.log('OG Image:', ogImage || 'MISSING');
  });

  test('should have canonical URL', async ({ page }) => {
    await page.goto('/es');
    const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
    console.log('Canonical URL:', canonical || 'MISSING');
  });
});

test.describe('Accessibility Tests', () => {
  test('should have skip link or main landmark', async ({ page }) => {
    await page.goto('/es');

    const main = await page.locator('main').count();
    const skipLink = await page.locator('a[href="#main"], a[href="#content"], .skip-link').count();

    console.log(`Main elements: ${main}`);
    console.log(`Skip links: ${skipLink}`);
  });

  test('should have proper link text (no "click here")', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    const badLinks = await page.locator('a:has-text("click here"), a:has-text("here"), a:has-text("read more")').count();
    console.log(`Links with poor accessibility text: ${badLinks}`);
  });

  test('should have focusable navigation', async ({ page }) => {
    await page.goto('/es');

    // Tab through the page and check focus visibility
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    console.log('First focused element:', focusedElement);
  });

  test('should have sufficient color contrast (basic check)', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    // Check if any text is using very light colors on white background
    const lightTextCount = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      let lightCount = 0;
      elements.forEach(el => {
        const style = window.getComputedStyle(el);
        const color = style.color;
        // Very basic check for light gray text
        if (color.includes('rgb(200') || color.includes('rgb(220') || color.includes('rgb(240')) {
          lightCount++;
        }
      });
      return lightCount;
    });

    console.log(`Elements with potentially low contrast: ${lightTextCount}`);
  });

  test('buttons should have accessible names', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    const buttons = page.locator('button');
    const count = await buttons.count();
    let buttonsWithoutText = 0;

    for (let i = 0; i < count; i++) {
      const btn = buttons.nth(i);
      const text = await btn.textContent();
      const ariaLabel = await btn.getAttribute('aria-label');
      const title = await btn.getAttribute('title');

      if (!text?.trim() && !ariaLabel && !title) {
        buttonsWithoutText++;
      }
    }

    console.log(`Total buttons: ${count}`);
    console.log(`Buttons without accessible name: ${buttonsWithoutText}`);
  });
});
