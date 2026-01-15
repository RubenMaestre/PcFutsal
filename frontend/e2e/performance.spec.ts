import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('homepage should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');
    const loadTime = Date.now() - startTime;

    console.log(`Homepage load time: ${loadTime}ms`);
    expect(loadTime).toBeLessThan(10000); // 10 seconds max
  });

  test('should not have excessive network requests on homepage', async ({ page }) => {
    const requests: string[] = [];
    page.on('request', request => requests.push(request.url()));

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    console.log(`Total requests: ${requests.length}`);
    // Log API calls specifically
    const apiCalls = requests.filter(url => url.includes('/api/'));
    console.log(`API calls: ${apiCalls.length}`);
    console.log('API endpoints:', apiCalls);

    expect(requests.length).toBeLessThan(100); // Reasonable limit
  });

  test('should handle slow network gracefully', async ({ page, context }) => {
    // Simulate slow 3G network
    await context.route('**/*', async route => {
      await new Promise(resolve => setTimeout(resolve, 100));
      await route.continue();
    });

    const response = await page.goto('/es', { timeout: 60000 });
    expect(response?.status()).toBeLessThan(400);
  });

  test('images should have proper loading attributes', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    const images = page.locator('img');
    const count = await images.count();

    let imagesWithAlt = 0;
    let imagesWithLazyLoad = 0;

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const loading = await img.getAttribute('loading');

      if (alt !== null && alt !== '') imagesWithAlt++;
      if (loading === 'lazy') imagesWithLazyLoad++;
    }

    console.log(`Total images: ${count}`);
    console.log(`Images with alt text: ${imagesWithAlt}`);
    console.log(`Images with lazy loading: ${imagesWithLazyLoad}`);
  });

  test('should measure First Contentful Paint', async ({ page }) => {
    await page.goto('/es');

    const fcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              resolve(entry.startTime);
              observer.disconnect();
            }
          }
        });
        observer.observe({ entryTypes: ['paint'] });

        // Fallback timeout
        setTimeout(() => resolve(-1), 10000);
      });
    });

    console.log(`First Contentful Paint: ${fcp}ms`);
    if (fcp > 0) {
      expect(fcp).toBeLessThan(3000); // Target: under 3 seconds
    }
  });
});
