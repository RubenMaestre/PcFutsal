import { test, expect } from '@playwright/test';

test.describe('Deep Performance Analysis', () => {
  test('analyze all network requests on homepage', async ({ page }) => {
    const requests: { url: string; type: string; size: number; time: number }[] = [];
    const startTime = Date.now();

    page.on('response', async response => {
      const request = response.request();
      let size = 0;
      try {
        const buffer = await response.body();
        size = buffer.length;
      } catch (e) {
        // Some responses can't be read
      }

      requests.push({
        url: response.url(),
        type: request.resourceType(),
        size: size,
        time: Date.now() - startTime
      });
    });

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    // Group by type
    const byType: { [key: string]: { count: number; totalSize: number } } = {};
    requests.forEach(r => {
      if (!byType[r.type]) byType[r.type] = { count: 0, totalSize: 0 };
      byType[r.type].count++;
      byType[r.type].totalSize += r.size;
    });

    console.log('\n=== NETWORK REQUESTS BY TYPE ===');
    Object.entries(byType).forEach(([type, data]) => {
      console.log(`${type}: ${data.count} requests, ${(data.totalSize / 1024).toFixed(1)} KB`);
    });

    // Show largest requests
    const sorted = [...requests].sort((a, b) => b.size - a.size);
    console.log('\n=== TOP 15 LARGEST REQUESTS ===');
    sorted.slice(0, 15).forEach(r => {
      const shortUrl = r.url.length > 80 ? r.url.substring(0, 80) + '...' : r.url;
      console.log(`${(r.size / 1024).toFixed(1)} KB - ${r.type} - ${shortUrl}`);
    });

    // Show slowest requests (by completion time)
    const bySlow = [...requests].sort((a, b) => b.time - a.time);
    console.log('\n=== SLOWEST REQUESTS (by completion time) ===');
    bySlow.slice(0, 10).forEach(r => {
      const shortUrl = r.url.length > 60 ? r.url.substring(0, 60) + '...' : r.url;
      console.log(`${r.time}ms - ${r.type} - ${shortUrl}`);
    });

    // Total stats
    const totalSize = requests.reduce((sum, r) => sum + r.size, 0);
    console.log(`\n=== TOTAL ===`);
    console.log(`Total requests: ${requests.length}`);
    console.log(`Total size: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  });

  test('analyze API calls specifically', async ({ page }) => {
    const apiCalls: { url: string; method: string; status: number; size: number; duration: number }[] = [];

    page.on('response', async response => {
      if (response.url().includes('/api/')) {
        const startTime = response.request().timing().startTime;
        let size = 0;
        try {
          const buffer = await response.body();
          size = buffer.length;
        } catch (e) {}

        apiCalls.push({
          url: response.url(),
          method: response.request().method(),
          status: response.status(),
          size: size,
          duration: response.request().timing().responseEnd
        });
      }
    });

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    console.log('\n=== API CALLS ANALYSIS ===');
    console.log(`Total API calls: ${apiCalls.length}`);

    apiCalls.forEach(api => {
      const endpoint = api.url.split('/api/')[1] || api.url;
      console.log(`\n${api.method} /api/${endpoint}`);
      console.log(`  Status: ${api.status}`);
      console.log(`  Size: ${(api.size / 1024).toFixed(1)} KB`);
    });

    // Check for duplicate or similar API calls
    const endpoints = apiCalls.map(a => a.url.split('?')[0]);
    const duplicates = endpoints.filter((item, index) => endpoints.indexOf(item) !== index);
    if (duplicates.length > 0) {
      console.log('\n=== POTENTIAL DUPLICATE API CALLS ===');
      [...new Set(duplicates)].forEach(d => console.log(d));
    }
  });

  test('measure Core Web Vitals', async ({ page }) => {
    await page.goto('/es');

    const metrics = await page.evaluate(() => {
      return new Promise<any>((resolve) => {
        const results: any = {};

        // Get performance entries
        const paintEntries = performance.getEntriesByType('paint');
        paintEntries.forEach(entry => {
          results[entry.name] = entry.startTime;
        });

        // Navigation timing
        const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (nav) {
          results['DNS Lookup'] = nav.domainLookupEnd - nav.domainLookupStart;
          results['TCP Connection'] = nav.connectEnd - nav.connectStart;
          results['TLS Handshake'] = nav.secureConnectionStart > 0 ? nav.connectEnd - nav.secureConnectionStart : 0;
          results['Time to First Byte (TTFB)'] = nav.responseStart - nav.requestStart;
          results['Content Download'] = nav.responseEnd - nav.responseStart;
          results['DOM Interactive'] = nav.domInteractive;
          results['DOM Complete'] = nav.domComplete;
          results['Load Event'] = nav.loadEventEnd;
        }

        // LCP observation
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          results['Largest Contentful Paint (LCP)'] = lastEntry.startTime;
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // CLS observation
        let clsScore = 0;
        const clsObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsScore += entry.value;
            }
          });
          results['Cumulative Layout Shift (CLS)'] = clsScore;
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });

        // Wait and resolve
        setTimeout(() => {
          lcpObserver.disconnect();
          clsObserver.disconnect();
          resolve(results);
        }, 5000);
      });
    });

    console.log('\n=== CORE WEB VITALS & TIMING ===');
    Object.entries(metrics).forEach(([key, value]) => {
      if (typeof value === 'number') {
        console.log(`${key}: ${(value as number).toFixed(2)}ms`);
      }
    });

    // Evaluate against thresholds
    console.log('\n=== PERFORMANCE ASSESSMENT ===');
    if (metrics['Largest Contentful Paint (LCP)']) {
      const lcp = metrics['Largest Contentful Paint (LCP)'];
      if (lcp <= 2500) console.log(`LCP: GOOD (${lcp.toFixed(0)}ms <= 2500ms)`);
      else if (lcp <= 4000) console.log(`LCP: NEEDS IMPROVEMENT (${lcp.toFixed(0)}ms <= 4000ms)`);
      else console.log(`LCP: POOR (${lcp.toFixed(0)}ms > 4000ms)`);
    }

    if (metrics['Time to First Byte (TTFB)']) {
      const ttfb = metrics['Time to First Byte (TTFB)'];
      if (ttfb <= 800) console.log(`TTFB: GOOD (${ttfb.toFixed(0)}ms <= 800ms)`);
      else if (ttfb <= 1800) console.log(`TTFB: NEEDS IMPROVEMENT (${ttfb.toFixed(0)}ms <= 1800ms)`);
      else console.log(`TTFB: POOR (${ttfb.toFixed(0)}ms > 1800ms)`);
    }

    if (metrics['Cumulative Layout Shift (CLS)'] !== undefined) {
      const cls = metrics['Cumulative Layout Shift (CLS)'];
      if (cls <= 0.1) console.log(`CLS: GOOD (${cls.toFixed(3)} <= 0.1)`);
      else if (cls <= 0.25) console.log(`CLS: NEEDS IMPROVEMENT (${cls.toFixed(3)} <= 0.25)`);
      else console.log(`CLS: POOR (${cls.toFixed(3)} > 0.25)`);
    }
  });

  test('check render blocking resources', async ({ page }) => {
    const blockingResources: string[] = [];

    page.on('response', async response => {
      const url = response.url();
      const type = response.request().resourceType();

      // Check for render-blocking CSS and JS
      if (type === 'stylesheet' || type === 'script') {
        const headers = response.headers();
        // Scripts without async/defer in head are blocking
        blockingResources.push(`${type}: ${url}`);
      }
    });

    await page.goto('/es');
    await page.waitForLoadState('domcontentloaded');

    // Check for inline scripts and styles
    const inlineStats = await page.evaluate(() => {
      const scripts = document.querySelectorAll('script');
      const styles = document.querySelectorAll('style');
      const links = document.querySelectorAll('link[rel="stylesheet"]');

      let inlineScriptSize = 0;
      let inlineStyleSize = 0;

      scripts.forEach(s => {
        if (s.innerHTML) inlineScriptSize += s.innerHTML.length;
      });
      styles.forEach(s => {
        inlineStyleSize += s.innerHTML.length;
      });

      return {
        totalScripts: scripts.length,
        totalStyles: styles.length,
        totalStylesheets: links.length,
        inlineScriptSize,
        inlineStyleSize
      };
    });

    console.log('\n=== RENDER BLOCKING ANALYSIS ===');
    console.log(`Total script tags: ${inlineStats.totalScripts}`);
    console.log(`Total style tags: ${inlineStats.totalStyles}`);
    console.log(`External stylesheets: ${inlineStats.totalStylesheets}`);
    console.log(`Inline script size: ${(inlineStats.inlineScriptSize / 1024).toFixed(1)} KB`);
    console.log(`Inline style size: ${(inlineStats.inlineStyleSize / 1024).toFixed(1)} KB`);
  });

  test('analyze images', async ({ page }) => {
    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    const imageAnalysis = await page.evaluate(() => {
      const images = document.querySelectorAll('img');
      const results: any[] = [];

      images.forEach(img => {
        results.push({
          src: img.src.substring(0, 100),
          naturalWidth: img.naturalWidth,
          naturalHeight: img.naturalHeight,
          displayWidth: img.clientWidth,
          displayHeight: img.clientHeight,
          loading: img.loading,
          hasAlt: !!img.alt,
          inViewport: img.getBoundingClientRect().top < window.innerHeight
        });
      });

      return results;
    });

    console.log('\n=== IMAGE ANALYSIS ===');
    console.log(`Total images: ${imageAnalysis.length}`);

    const lazyLoaded = imageAnalysis.filter(i => i.loading === 'lazy').length;
    const withAlt = imageAnalysis.filter(i => i.hasAlt).length;
    const oversized = imageAnalysis.filter(i =>
      i.naturalWidth > i.displayWidth * 2 || i.naturalHeight > i.displayHeight * 2
    );

    console.log(`Lazy loaded: ${lazyLoaded}/${imageAnalysis.length}`);
    console.log(`With alt text: ${withAlt}/${imageAnalysis.length}`);
    console.log(`Potentially oversized: ${oversized.length}`);

    if (oversized.length > 0) {
      console.log('\n=== OVERSIZED IMAGES ===');
      oversized.slice(0, 5).forEach(img => {
        console.log(`Natural: ${img.naturalWidth}x${img.naturalHeight}, Display: ${img.displayWidth}x${img.displayHeight}`);
        console.log(`  ${img.src}`);
      });
    }
  });

  test('check third-party scripts impact', async ({ page }) => {
    const thirdParty: { domain: string; count: number; size: number }[] = [];
    const domains: { [key: string]: { count: number; size: number } } = {};

    page.on('response', async response => {
      const url = new URL(response.url());
      const domain = url.hostname;

      if (!domain.includes('pcfutsal.es')) {
        if (!domains[domain]) domains[domain] = { count: 0, size: 0 };
        domains[domain].count++;

        try {
          const buffer = await response.body();
          domains[domain].size += buffer.length;
        } catch (e) {}
      }
    });

    await page.goto('/es');
    await page.waitForLoadState('networkidle');

    console.log('\n=== THIRD-PARTY SCRIPTS ===');
    const sorted = Object.entries(domains).sort((a, b) => b[1].size - a[1].size);
    sorted.forEach(([domain, data]) => {
      console.log(`${domain}: ${data.count} requests, ${(data.size / 1024).toFixed(1)} KB`);
    });

    const totalThirdParty = Object.values(domains).reduce((sum, d) => sum + d.size, 0);
    console.log(`\nTotal third-party: ${(totalThirdParty / 1024).toFixed(1)} KB`);
  });
});
