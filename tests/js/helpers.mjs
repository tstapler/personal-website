// Shared harness: build the site with Hugo, serve it statically, drive system Chrome.
import { chromium } from 'playwright-core'
import { spawn } from 'node:child_process'
import fs from 'node:fs'
import http from 'node:http'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const MIME = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.xml': 'application/xml', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.ico': 'image/x-icon', '.txt': 'text/plain',
}

/** Build the site with Hugo into a temp dir and serve it. `env` overrides process.env (e.g. HUGO_ENV). */
export async function buildAndServe(env = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'site-test-'))
  const server = http.createServer((req, res) => {
    let p = path.join(dir, decodeURIComponent(new URL(req.url, 'http://x').pathname))
    if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html')
    if (!fs.existsSync(p)) { res.writeHead(404).end('not found'); return }
    res.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' })
    fs.createReadStream(p).pipe(res)
  })
  await new Promise((r) => server.listen(0, '127.0.0.1', r))
  const url = `http://127.0.0.1:${server.address().port}`

  // Set the HUGO_THEME env var to run this suite against the alternate Fomantic theme.
  // config.toml pins assetDir to the espouse theme, so the theme's JS/CSS bundles must be redirected too.
  const theme = process.env.HUGO_THEME
  const args = ['--quiet', '--destination', dir, '--baseURL', url, ...(theme ? ['--theme', theme] : [])]
  const full = { ...process.env, ...(theme ? { HUGO_ASSETDIR: `themes/${theme}/static` } : {}), ...env }
  // Async on purpose: a blocking exec would starve the in-process server that Hugo's PostCSS may fetch from.
  const close = async () => { server.close(); fs.rmSync(dir, { recursive: true, force: true }) }
  try {
    await new Promise((resolve, reject) => {
      const child = spawn('hugo', args, { cwd: ROOT, stdio: 'inherit', env: full })
      child.on('error', reject)
      child.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`hugo exited with ${code}`))))
    })
  } catch (e) {
    await close() // a leaked listener would keep the test process alive until its timeout
    throw e
  }
  return { url, close }
}

/** Serve BASE_URL if set, otherwise build the site (honours HUGO_ENV / HUGO_THEME) and serve that. */
export async function startSite() {
  if (process.env.BASE_URL) return { url: process.env.BASE_URL.replace(/\/$/, ''), close: async () => {} }
  return buildAndServe()
}

function chromePath() {
  const candidates = [process.env.CHROME_PATH, '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome',
    '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
  const found = candidates.find((c) => c && fs.existsSync(c))
  if (!found) throw new Error('No Chrome found; set CHROME_PATH')
  return found
}

export const launch = () => chromium.launch({ executablePath: chromePath(), headless: true })

/** Collect uncaught exceptions, console errors, and same-origin 4xx/5xx responses. */
export function trackErrors(page, origin) {
  const errors = []
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`))
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`console: ${m.text()}`) })
  page.on('response', (r) => {
    if (r.url().startsWith(origin) && r.status() >= 400) errors.push(`${r.status()} ${r.url()}`)
  })
  return errors
}

export async function sitemapPaths(origin) {
  const xml = await (await fetch(`${origin}/sitemap.xml`)).text()
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname)
}
