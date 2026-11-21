// Bazel post-build step: purge + minify the site's stylesheet against the HTML/JS Hugo actually rendered,
// then re-fingerprint it and update the <link> tags. Usage: node optimize_site.mjs <site dir> <out dir>
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'

const require = createRequire(import.meta.url)
const postcss = require('postcss')
const autoprefixer = require('autoprefixer')
const cssnano = require('cssnano')
const purgecss = require('@fullhuman/postcss-purgecss')
const { purgeOptions } = require('./postcss.shared.js')

// Under Bazel, paths are relative to the execroot (rules_js starts the tool inside a sandbox-relative cwd).
const base = process.env.JS_BINARY__EXECROOT || process.cwd()
const [siteDir, outDir] = process.argv.slice(2).map((p) => path.resolve(base, p))
if (!process.argv[3]) throw new Error('usage: optimize_site.mjs <site dir> <out dir>')

fs.rmSync(outDir, { recursive: true, force: true })
// Real copies (not symlinks or hardlinks into the read-only Bazel inputs), so they can be rewritten.
for (const f of walk(siteDir)) {
  const dest = path.join(outDir, path.relative(siteDir, f))
  fs.mkdirSync(path.dirname(dest), { recursive: true })
  fs.writeFileSync(dest, fs.readFileSync(f))
}

const cssPath = walk(outDir).find((f) => /\/css\/site\.[0-9a-f]+\.css$/.test(f))
if (!cssPath) throw new Error(`no css/site.<hash>.css under ${outDir}`)

const result = await postcss([
  autoprefixer(),
  purgecss(purgeOptions([`${outDir}/**/*.html`, `${outDir}/js/*.js`])),
  cssnano({ preset: ['default', { discardComments: { removeAll: true } }] }),
]).process(fs.readFileSync(cssPath, 'utf8'), { from: cssPath, to: cssPath })

const digest = createHash('sha512').update(result.css).digest()
const newName = `site.${digest.toString('hex')}.css`
const oldName = path.basename(cssPath)
fs.rmSync(cssPath)
fs.writeFileSync(path.join(path.dirname(cssPath), newName), result.css)

const integrity = `sha512-${digest.toString('base64')}`
let rewritten = 0
for (const f of walk(outDir).filter((p) => p.endsWith('.html'))) {
  const html = fs.readFileSync(f, 'utf8')
  if (!html.includes(oldName)) continue
  const next = html.replace(/<link\b[^>]*>/g, (tag) =>
    tag.includes(oldName) ? tag.replaceAll(oldName, newName).replace(/integrity="[^"]*"/, `integrity="${integrity}"`) : tag)
  fs.writeFileSync(f, next)
  rewritten++
}
console.log(`optimize_site: ${oldName.slice(0, 16)}… ${fs.statSync(path.join(path.dirname(cssPath), newName)).size} bytes, ${rewritten} pages updated`)

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)])
}
