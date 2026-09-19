import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8787';
const output = path.resolve('assets-private/film-v2/qa');
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const results = [];
try {
  for (const viewport of [{ width: 1600, height: 1100 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    // External GS viewer is unrelated to local media framing and uses a large GPU scene.
    await page.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base, { waitUntil: 'domcontentloaded' });
    const sectionAudit = await page.evaluate(() => ({
      firstSections: [...document.querySelectorAll('main > section.section-band')].slice(0, 3).map(section => section.id || section.classList[1]),
      systemTitle: document.querySelector('#system h2')?.textContent,
      filmTitle: document.querySelector('#film h2')?.textContent,
      routeTitle: document.querySelector('#route h2')?.textContent,
      evidenceTitle: document.querySelector('#evidence h2')?.textContent,
    }));
    if (JSON.stringify(sectionAudit.firstSections) !== JSON.stringify(['system', 'film', 'mission-section'])
      || sectionAudit.systemTitle !== '可靠定位助力视觉语言导航落地园区巡检'
      || sectionAudit.filmTitle !== '完整方案讲解'
      || sectionAudit.routeTitle !== '逐路段模型推理回放'
      || sectionAudit.evidenceTitle !== '模型推理量化结果') {
      throw new Error(JSON.stringify({ sectionAudit }));
    }
    await page.evaluate(() => document.querySelector('.hero-stage video')?.pause());
    const heroAudit = await page.evaluate(() => {
      const hero = document.querySelector('.hero-stage');
      const rect = hero.getBoundingClientRect();
      return {
        title: hero.querySelector('h1')?.innerText,
        statement: hero.querySelector('.hero-statement')?.innerText,
        bottom: rect.bottom,
        viewportHeight: innerHeight,
      };
    });
    if (heroAudit.title !== '视觉语言导航\n园区巡检系统' || heroAudit.statement !== '让视觉语言导航真正落地园区巡检' || heroAudit.bottom > heroAudit.viewportHeight + 1) {
      throw new Error(JSON.stringify({ heroAudit }));
    }
    await page.screenshot({ path: path.join(output, `page-hero-${viewport.width}.png`) });
    await page.locator('#system').evaluate(section => {
      document.documentElement.style.scrollBehavior = 'auto';
      window.scrollTo(0, window.scrollY + section.getBoundingClientRect().top - 64);
    });
    await page.screenshot({ path: path.join(output, `page-system-title-${viewport.width}.png`) });
    await page.waitForFunction(() => {
      const film = document.querySelector('.feature-film');
      return film && film.readyState >= 2 && film.duration === 64;
    });
    await page.locator('.feature-film').scrollIntoViewIfNeeded();
    await page.evaluate(async () => {
      const film = document.querySelector('.feature-film');
      film.muted = true;
      await film.play();
    });
    await page.waitForFunction(() => document.querySelector('.feature-film').currentTime > 0.1);
    await page.evaluate(() => new Promise(resolve => {
      const film = document.querySelector('.feature-film');
      film.pause();
      film.addEventListener('seeked', resolve, { once: true });
      film.currentTime = 42;
    }));
    await page.waitForTimeout(300);
    const audit = await page.evaluate(() => {
      const film = document.querySelector('.feature-film');
      const route = document.querySelector('.route-media video');
      const label = document.querySelector('.route-media-label');
      const videoRect = route.getBoundingClientRect();
      const labelRect = label.getBoundingClientRect();
      return {
        width: innerWidth,
        documentWidth: document.documentElement.scrollWidth,
        duration: film.duration,
        currentTime: film.currentTime,
        readyState: film.readyState,
        videoSize: [film.videoWidth, film.videoHeight],
        filmFit: getComputedStyle(film).objectFit,
        routeFit: getComputedStyle(route).objectFit,
        routeLabelOutsideVideo: labelRect.top >= videoRect.bottom - 1,
        filmSource: film.currentSrc,
        captions: [...film.querySelectorAll('track')].map(x => x.src),
        oldTerminology: document.body.innerText.includes('数字孪生'),
      };
    });
    if (Math.abs(audit.currentTime - 42) > 0.1 || audit.readyState < 2 || audit.documentWidth > viewport.width + 1 || audit.filmFit !== 'contain' || audit.routeFit !== 'contain' || !audit.routeLabelOutsideVideo || audit.oldTerminology || errors.length) {
      throw new Error(JSON.stringify({ audit, errors }));
    }
    await page.screenshot({ path: path.join(output, `page-film-${viewport.width}.png`) });
    if (viewport.width > 1000) {
      await page.locator('.route-map-figure').scrollIntoViewIfNeeded();
      await page.locator('.route-map-figure img').evaluate(img => img.decode());
      await page.screenshot({ path: path.join(output, 'page-mission-desktop.png') });
      await page.locator('.architecture-diagram').scrollIntoViewIfNeeded();
      await page.locator('.architecture-diagram img').evaluate(img => img.decode());
      await page.screenshot({ path: path.join(output, 'page-framework-desktop.png') });
      await page.locator('.open-section').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(output, 'page-repository-desktop.png') });
      await page.locator('.route-strip button').nth(11).click();
      await page.waitForFunction(() => document.querySelector('.route-head p')?.textContent === 'SEGMENT 12');
      const epoch2Source = await page.locator('.route-media source').getAttribute('src');
      await page.locator('.segmented button').first().click();
      await page.waitForFunction(() => document.querySelector('.route-media-label span')?.textContent?.includes('EPOCH1'));
      const epoch1Source = await page.locator('.route-media source').getAttribute('src');
      if (!epoch2Source?.endsWith('.mp4') || !epoch1Source?.endsWith('.mp4') || epoch1Source === epoch2Source) {
        throw new Error(JSON.stringify({ epoch1Source, epoch2Source }));
      }
    } else {
      await page.locator('.route-map-figure').scrollIntoViewIfNeeded();
      await page.locator('.route-map-figure img').evaluate(img => img.decode());
      await page.screenshot({ path: path.join(output, 'page-mission-mobile.png') });
      await page.locator('.open-section').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(output, 'page-repository-mobile.png') });
    }
    results.push({ ...audit, hero: heroAudit, errors });
    await page.close();
  }
  await writeFile(path.join(output, 'browser-validation.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
} finally {
  await browser.close();
}
