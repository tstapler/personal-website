// Whole-site crawl (no JS errors, no broken local assets) and a device matrix that uses
// Chrome DevTools Protocol emulation for viewport / touch / DPR.
import { after, before, describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { devices } from 'playwright-core'
import { launch, sitemapPaths, startSite, trackErrors } from './helpers.mjs'

let site, browser
before(async () => { site = await startSite(); browser = await launch() })
after(async () => { await browser?.close(); await site?.close() })

describe('site crawl', () => {
  it('every sitemap page loads with no JS errors and no 4xx/5xx local assets', async () => {
    let paths = await sitemapPaths(site.url)
    // /search needs a Pagefind index (`make search`); skip it when the index is absent.
    const hasPagefind = (await fetch(site.url + '/pagefind/pagefind-ui.js')).ok
    if (!hasPagefind) paths = paths.filter((p) => !p.startsWith('/search'))
    assert.ok(paths.length > 10, `sitemap only had ${paths.length} URLs`)
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } })
    const failures = []
    for (const p of paths) {
      const page = await context.newPage()
      const errors = trackErrors(page, site.url)
      const res = await page.goto(site.url + p, { waitUntil: 'load' })
      if (!res.ok()) errors.push(`page status ${res.status()}`)
      // Third-party noise (analytics, CDN fonts) is not ours to fix here.
      const ours = errors.filter((e) => !/googletagmanager|google-analytics|net::ERR/.test(e) && !KNOWN_BROKEN.some((k) => k.test(e)))
      // Chrome also logs a generic console line for each failed resource; drop it once the 404 itself is allowlisted.
      if (!errors.some((e) => /^\d{3} /.test(e) && !KNOWN_BROKEN.some((k) => k.test(e)))) {
        for (let i = ours.length - 1; i >= 0; i--) if (/Failed to load resource/.test(ours[i])) ours.splice(i, 1)
      }
      if (ours.length) failures.push(`${p}\n    ${ours.join('\n    ')}`)
      await page.close()
    }
    await context.close()
    assert.deepEqual(failures, [], `${failures.length}/${paths.length} pages had errors:\n${failures.join('\n')}`)
  })
})

// Known-broken asset, referenced by content/projects/peeps; remove once the image is restored.
const KNOWN_BROKEN = [/\/img\/peeps-screenshot\.jpg/]

const MATRIX = [
  ['iPhone 13', devices['iPhone 13']],
  ['Pixel 7', devices['Pixel 7']],
  ['iPad Mini', devices['iPad Mini']],
  ['Desktop 1280', { viewport: { width: 1280, height: 800 } }],
]
const PAGES = ['/', '/blog/', '/blog/manifest-driven-development/', '/projects/']

// Elements that may legitimately scroll internally.
// .ui.cards has Semantic UI's intentional negative gutter margin (clipped, not scrollable).
const SCROLLERS = 'pre, .highlight, table, .mermaid, .toc-wrapper, .ui.cards, .ui.main.menu, [class*="marquee"], #particles-js canvas'

describe('device matrix (CDP emulation)', () => {
  for (const [name, device] of MATRIX) {
    for (const path of PAGES) {
      it(`${name} ${path}: no horizontal overflow, correct nav mode`, async () => {
        const context = await browser.newContext({ ...device, colorScheme: 'light' })
        const page = await context.newPage()
        await page.goto(site.url + path, { waitUntil: 'load' })

        const r = await page.evaluate((scrollers) => {
          const vw = document.documentElement.clientWidth
          const offenders = [...document.body.querySelectorAll('*')]
            .filter((e) => !e.closest(scrollers) && e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > vw + 1)
            .slice(0, 5)
            .map((e) => `${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}.${[...e.classList].slice(0, 2).join('.')} right=${Math.round(e.getBoundingClientRect().right)} vw=${vw}`)
          const desktopLinks = document.querySelector('.nav-desktop-links')
          return {
            vw,
            offenders,
            desktopLinksVisible: !!desktopLinks && getComputedStyle(desktopLinks).display !== 'none',
            menuButtonVisible: !!document.querySelector('#menuButton')?.offsetParent,
          }
        }, SCROLLERS)

        assert.deepEqual(r.offenders, [], 'elements stick out past the viewport')
        assert.equal(r.desktopLinksVisible, r.vw >= 768, `desktop nav links at ${r.vw}px`)
        assert.ok(r.menuButtonVisible, 'menu button hidden')
        await context.close()
      })
    }
  }

  for (const name of ['iPhone 13', 'Pixel 7']) {
    it(`${name}: top bar (incl. theme toggle) fits inside the viewport`, async () => {
      const context = await browser.newContext(devices[name])
      const page = await context.newPage()
      await page.goto(site.url + '/', { waitUntil: 'load' })
      const r = await page.evaluate(() => ({
        vw: document.documentElement.clientWidth,
        toggleRight: Math.round(document.querySelector('.theme-toggle').getBoundingClientRect().right),
      }))
      assert.ok(r.toggleRight <= r.vw, `theme toggle right edge ${r.toggleRight} > viewport ${r.vw}`)
      await context.close()
    })
  }

  it('raw CDP Emulation.setDeviceMetricsOverride switches the layout live', async () => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } })
    const page = await context.newPage()
    await page.goto(site.url + '/')
    const cdp = await context.newCDPSession(page)
    const width = () => page.evaluate(() => innerWidth)
    const linksShown = () => page.evaluate(() => getComputedStyle(document.querySelector('.nav-desktop-links')).display !== 'none')

    assert.equal(await width(), 1280)
    assert.equal(await linksShown(), true)

    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 3, mobile: true })
    await page.waitForTimeout(200)
    assert.equal(await width(), 375)
    assert.equal(await linksShown(), false)

    await cdp.send('Emulation.clearDeviceMetricsOverride')
    await context.close()
  })

  it('mobile: sidebar opens by tap and covers a usable part of the screen', async () => {
    const context = await browser.newContext({ ...devices['iPhone 13'] })
    const page = await context.newPage()
    await page.goto(site.url + '/')
    await page.tap('#menuButton')
    await page.locator('.ui.sidebar').waitFor({ state: 'visible' })
    const box = await page.locator('.ui.sidebar').boundingBox()
    assert.ok(box.width > 60 && box.width < 390, `sidebar width ${box.width}`)
    await context.close()
  })
})
