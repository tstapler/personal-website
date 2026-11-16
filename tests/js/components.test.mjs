// Integration tests for the site's JS components (theme toggle, sidebar, sticky nav,
// copy buttons, heading anchors, progress bar, TOC highlight, lightbox, canvas, mermaid).
// Run: npm run test:js   (BASE_URL=http://localhost:1313 to reuse a running server)
import { after, before, describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { launch, startSite, trackErrors } from './helpers.mjs'

const POST = '/blog/manifest-driven-development/'
const IMAGE_POST = '/blog/the_powerline_effect/'
const CODE_POST = '/blog/structured-concurrency-footgun/'

let site, browser

before(async () => { site = await startSite(); browser = await launch() })
after(async () => { await browser?.close(); await site?.close() })

/** Fresh context per test so localStorage and prefers-color-scheme never leak. */
async function open(path, opts = {}) {
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    colorScheme: 'light',
    permissions: ['clipboard-read', 'clipboard-write'],
    ...opts,
  })
  const page = await context.newPage()
  const errors = trackErrors(page, site.url)
  await page.goto(site.url + path, { waitUntil: 'load' })
  return { page, context, errors }
}

describe('theme toggle', () => {
  it('follows system preference when nothing is saved', async () => {
    const { page, context } = await open('/', { colorScheme: 'dark' })
    assert.equal(await page.getAttribute('html', 'data-theme'), 'dark')
    assert.equal(await page.getAttribute('meta[name=theme-color]', 'content'), '#1a1a1a')
    await context.close()
  })

  it('toggles on click, persists, fires themechange, and survives reload', async () => {
    const { page, context } = await open('/')
    await page.evaluate(() => { window.__events = []; addEventListener('themechange', (e) => __events.push(e.detail.theme)) })
    assert.equal(await page.getAttribute('html', 'data-theme'), 'light')

    await page.click('.theme-toggle')
    assert.equal(await page.getAttribute('html', 'data-theme'), 'dark')
    assert.equal(await page.evaluate(() => localStorage.getItem('theme-preference')), 'dark')
    assert.deepEqual(await page.evaluate(() => __events), ['dark'])

    await page.reload()
    assert.equal(await page.getAttribute('html', 'data-theme'), 'dark')
    await context.close()
  })

  it('toggles from the keyboard and saved choice beats system preference', async () => {
    const { page, context } = await open('/', { colorScheme: 'dark' })
    await page.focus('.theme-toggle')
    await page.keyboard.press('Enter')
    assert.equal(await page.getAttribute('html', 'data-theme'), 'light')
    await page.reload()
    assert.equal(await page.getAttribute('html', 'data-theme'), 'light')
    await context.close()
  })

  it('actually changes rendered colors', async () => {
    const { page, context } = await open(POST)
    const bg = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor)
    const before = await bg()
    await page.click('.theme-toggle')
    await page.waitForFunction((b) => getComputedStyle(document.body).backgroundColor !== b, before, { timeout: 3000 })
    await context.close()
  })
})

describe('navigation', () => {
  it('menu button opens the sidebar and sets aria-expanded', async () => {
    const { page, context } = await open('/')
    const btn = page.locator('#menuButton')
    assert.equal(await btn.getAttribute('aria-expanded'), 'false')
    await btn.click()
    await page.locator('.ui.sidebar.visible').waitFor()
    assert.equal(await btn.getAttribute('aria-expanded'), 'true')
    await context.close()
  })

  it('closing the sidebar by clicking where the menu button is resets aria-expanded', async () => {
    const { page, context } = await open('/')
    await page.click('#menuButton')
    await page.locator('.ui.sidebar.visible').waitFor()
    await page.waitForTimeout(600) // let the push animation settle so the click lands on the dimmer
    const box = await page.locator('#menuButton').boundingBox()
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2)
    await page.locator('.ui.sidebar.visible').waitFor({ state: 'detached' })
    assert.equal(await page.getAttribute('#menuButton', 'aria-expanded'), 'false')
    await context.close()
  })

  it('menu button works from the keyboard (Enter and Space)', async () => {
    const { page, context } = await open('/')
    await page.focus('#menuButton')
    await page.keyboard.press('Enter')
    await page.locator('.ui.sidebar.visible').waitFor()
    await page.keyboard.press('Space')
    await page.locator('.ui.sidebar.visible').waitFor({ state: 'detached' })
    await context.close()
  })

  it('sticky menu stays pinned to the top while scrolling a long post', async () => {
    const { page, context } = await open(POST)
    await page.mouse.wheel(0, 2500)
    await page.waitForTimeout(400)
    const box = await page.locator('.ui.main.menu').boundingBox()
    assert.ok(box && box.y >= -1 && box.y <= 1, `menu top was ${box?.y}`)
    await context.close()
  })
})

describe('post enhancements', () => {
  it('adds a heading anchor to every h2/h3 with an id', async () => {
    const { page, context } = await open(POST)
    const r = await page.evaluate(() => {
      const hs = [...document.querySelectorAll('#content h2[id], #content h3[id]')]
      return { total: hs.length, ok: hs.filter((h) => h.querySelector(`a.heading-anchor[href="#${h.id}"]`)).length }
    })
    assert.ok(r.total > 0)
    assert.equal(r.ok, r.total)
    await context.close()
  })

  it('copy button puts the code block text on the clipboard and shows feedback', async () => {
    const { page, context } = await open(CODE_POST)
    const pre = page.locator('article pre:not(.mermaid)').first()
    await pre.scrollIntoViewIfNeeded()
    await pre.hover()
    const btn = pre.locator('.copy-btn')
    const expected = await pre.evaluate((p) => (p.querySelector('code') || p).innerText)
    await btn.click()
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), expected)
    assert.match(await btn.textContent(), /Copied/)
    await page.waitForFunction(() => document.querySelector('.copy-btn').textContent === 'Copy', null, { timeout: 4000 })
    await context.close()
  })

  it('reading progress bar grows with scroll', async () => {
    const { page, context } = await open(POST)
    const scale = () => page.evaluate(() => new DOMMatrix(getComputedStyle(document.getElementById('reading-progress')).transform).a)
    assert.equal(await scale(), 0)
    await page.mouse.wheel(0, 3000) // real wheel input, as a reader would scroll
    await page.waitForTimeout(400)
    assert.ok((await scale()) > 0.1, `scale after scrolling was ${await scale()}`)
    await context.close()
  })

  it('TOC highlights the section currently in view', async () => {
    const { page, context } = await open(POST)
    const headings = await page.$$eval('#content h2[id]', (hs) => hs.map((h) => h.id))
    assert.ok(headings.length >= 3)
    const target = headings[2]
    const top = await page.evaluate((id) => document.getElementById(id).getBoundingClientRect().top, target)
    await page.mouse.wheel(0, top - 60)
    await page.waitForTimeout(400)
    const active = await page.$$eval('#TableOfContents a.toc-active', (as) => as.map((a) => a.getAttribute('href')))
    assert.deepEqual(active, [`#${target}`])
    await context.close()
  })

  it('wraps markdown tables in Semantic UI table classes', async () => {
    const { page, context } = await open(POST)
    const bad = await page.$$eval('#content table', (ts) => ts.filter((t) => !t.classList.contains('ui')).length)
    assert.equal(bad, 0)
    await context.close()
  })

  it('lightbox opens the full image in an overlay and removes it on close', async () => {
    const { page, context, errors } = await open(IMAGE_POST)
    const overlay = '.ui.modal, dialog.lightbox'
    const fig = page.locator('.post-image').first()
    await fig.scrollIntoViewIfNeeded()
    const src = await fig.locator('img').evaluate((i) => i.src)
    await fig.locator('img').click()

    await page.locator(overlay).first().waitFor({ state: 'visible' })
    assert.equal(await page.locator(overlay).first().locator('img').evaluate((i) => i.src), src)

    await page.waitForTimeout(600) // Semantic ignores Escape until its show transition finishes
    await page.keyboard.press('Escape')
    await page.waitForFunction((sel) => document.querySelectorAll(sel).length === 0, overlay, { timeout: 5000 })
    assert.deepEqual(errors, [])
    await context.close()
  })
})

describe('home page', () => {
  it('draws an animated dot field on the hero canvas, and keeps it sized on resize', async () => {
    const { page, context } = await open('/')
    const canvas = page.locator('#particles-js canvas')
    await canvas.waitFor({ state: 'attached' })
    const snap = () => page.evaluate(() => {
      const c = document.querySelector('#particles-js canvas')
      const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data
      let lit = 0
      for (let i = 3; i < d.length; i += 4) if (d[i]) lit++
      return { lit, w: c.width, h: c.height }
    })
    await page.waitForTimeout(300)
    const a = await snap()
    assert.ok(a.lit > 0, 'canvas is blank')
    await page.waitForTimeout(500)
    const b = await snap()
    assert.ok(b.lit > 0)

    await page.setViewportSize({ width: 700, height: 800 })
    await page.waitForTimeout(200)
    const resized = await snap()
    assert.ok(resized.w <= a.w, `canvas did not shrink (${a.w} -> ${resized.w})`)
    await context.close()
  })

  it('hero buttons navigate to the blog and projects', async () => {
    const { page, context } = await open('/')
    await page.click('text=Read My Blog')
    await page.waitForURL('**/blog/')
    await page.goBack()
    await page.click('text=View Projects')
    await page.waitForURL('**/projects/')
    await context.close()
  })
})

describe('mermaid diagrams (loads from jsdelivr CDN)', () => {
  it('renders pre.mermaid blocks to SVG', async (t) => {
    const online = await fetch('https://cdn.jsdelivr.net/npm/mermaid@11/package.json', { signal: AbortSignal.timeout(4000) })
      .then((r) => r.ok).catch(() => false)
    if (!online) return t.skip('jsdelivr unreachable')

    const { page, context } = await open(POST)
    const total = await page.locator('pre.mermaid').count()
    assert.ok(total > 0, 'post has no mermaid blocks')
    await page.waitForFunction((n) => document.querySelectorAll('pre.mermaid svg').length === n, total, { timeout: 20000 })
    await context.close()
  })
})
