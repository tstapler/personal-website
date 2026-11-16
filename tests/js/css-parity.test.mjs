// Guards CSS tree-shaking: the production build (PurgeCSS + minify) must render every page
// exactly like the unpurged development build. Compares the computed style of every element.
// Meaningful for any theme (HUGO_THEME), but only themes whose production pipeline purges aggressively
// can fail it.
import { after, before, describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { devices } from 'playwright-core'
import { buildAndServe, launch } from './helpers.mjs'

const PAGES = [
  '/', '/blog/', '/blog/manifest-driven-development/', '/blog/structured-concurrency-footgun/',
  '/blog/the_powerline_effect/', '/projects/', '/projects/peeps/', '/tags/', '/404.html',
]

const CONTEXTS = [
  ['desktop light', { viewport: { width: 1280, height: 800 }, colorScheme: 'light' }],
  ['mobile dark', { ...devices['iPhone 13'], colorScheme: 'dark' }],
]

// Static properties only: animated ones (transform, opacity) legitimately differ frame to frame.
const PROPS = ['display', 'position', 'color', 'backgroundColor', 'backgroundImage', 'fontSize', 'fontFamily',
  'fontWeight', 'lineHeight', 'letterSpacing', 'textAlign', 'textDecorationLine', 'textTransform',
  'marginTop', 'marginRight', 'marginBottom', 'marginLeft', 'paddingTop', 'paddingRight', 'paddingBottom',
  'paddingLeft', 'borderTopWidth', 'borderTopColor', 'borderTopStyle', 'borderBottomWidth', 'borderBottomColor',
  'borderRadius', 'boxShadow', 'width', 'height', 'overflowX', 'overflowY', 'visibility', 'zIndex',
  'flexDirection', 'flexWrap', 'justifyContent', 'alignItems', 'gap', 'cursor', 'animationName', 'listStyleType',
  'whiteSpace', 'verticalAlign', 'float', 'content']

/** Computed styles for every element, in document order, after fonts settle. */
async function snapshot(page) {
  // semanticExtras.css is preloaded and swapped to rel=stylesheet by onload, so it can land after `load`
  await page.waitForFunction(() => !document.querySelector('link[rel=preload][as=style]') &&
    [...document.querySelectorAll('link[rel=stylesheet]')].every((l) => l.sheet))
  await page.evaluate(() => document.fonts.ready)
  // Freeze in-flight hover/theme transitions so timing noise can't masquerade as a CSS difference
  await page.addStyleTag({ content: '*, *::before, *::after { transition: none !important }' })
  await page.waitForTimeout(500)
  return page.evaluate((props) => {
    const skip = 'canvas, .mermaid, #particles-js, [class*="marquee"] *'
    return [...document.body.querySelectorAll('*')]
      .filter((e) => !e.matches(skip) && !e.closest('canvas'))
      .map((e, i) => {
        const cs = getComputedStyle(e)
        const label = `${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 3).join('.') : ''}`
        return { i, label, s: props.map((p) => cs[p]) }
      })
  }, PROPS)
}

// cssnano rewrites colours into shorter equivalents that can differ by up to 2/255 per channel.
const rgbChannels = (v) => (typeof v === 'string' && v.startsWith('rgb') ? v.match(/[\d.]+/g)?.map(Number) : null)
function sameValue(x, y) {
  if (x === y) return true
  const [p, q] = [rgbChannels(x), rgbChannels(y)]
  return !!p && !!q && p.length === q.length && p.every((n, i) => Math.abs(n - q[i]) <= (i < 3 ? 2 : 0.011))
}

function diff(a, b, props) {
  const out = []
  if (a.length !== b.length) out.push(`element count differs: dev=${a.length} prod=${b.length}`)
  for (let k = 0; k < Math.min(a.length, b.length) && out.length < 12; k++) {
    props.forEach((p, j) => {
      if (!sameValue(a[k].s[j], b[k].s[j]) && out.length < 12) {
        out.push(`${a[k].label} [${a[k].i}] ${p}: dev=${JSON.stringify(a[k].s[j])} prod=${JSON.stringify(b[k].s[j])}`)
      }
    })
  }
  return out
}

let dev, prod, browser, skipReason
before(async () => {
  try {
    dev = await buildAndServe({ HUGO_ENV: 'development' })
    prod = await buildAndServe({ HUGO_ENV: 'production' })
    browser = await launch()
  } catch (e) {
    // e.g. the espouse theme's html_head still calls resources.PostCSS, which Hugo >= 0.128 removed.
    skipReason = `production build unavailable for this theme: ${e.message}`
  }
})
after(async () => { await browser?.close(); await dev?.close(); await prod?.close() })

async function compare(path, ctxOpts, interact) {
  const shots = []
  for (const site of [dev, prod]) {
    const context = await browser.newContext(ctxOpts)
    const page = await context.newPage()
    await page.goto(site.url + path, { waitUntil: 'networkidle' })
    if (interact) await interact(page)
    shots.push(await snapshot(page))
    await context.close()
  }
  return diff(shots[0], shots[1], PROPS)
}

describe('production (purged) CSS renders identically to development', () => {
  for (const [name, opts] of CONTEXTS) {
    for (const path of PAGES) {
      it(`${name} ${path}`, async (t) => {
        if (skipReason) return t.skip(skipReason)
        assert.deepEqual(await compare(path, opts), [])
      })
    }
  }

  it('sidebar open (desktop)', async (t) => {
    if (skipReason) return t.skip(skipReason)
    const open = async (page) => {
      await page.click('#menuButton')
      await page.locator('.ui.sidebar.visible').waitFor()
      await page.waitForTimeout(800)
    }
    assert.deepEqual(await compare('/', CONTEXTS[0][1], open), [])
  })

  it('lightbox modal open (desktop)', async (t) => {
    if (skipReason) return t.skip(skipReason)
    const open = async (page) => {
      await page.locator('.post-image img').first().click()
      await page.locator('.ui.modal, dialog.lightbox').first().waitFor({ state: 'visible' })
      await page.waitForTimeout(800)
    }
    assert.deepEqual(await compare('/blog/the_powerline_effect/', CONTEXTS[0][1], open), [])
  })
})
