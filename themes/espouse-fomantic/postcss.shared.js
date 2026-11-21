// Purge settings shared by Hugo's css.PostCSS (postcss.config.js) and the Bazel post-build step (optimize_site.mjs).
// Fomantic styles many things with attribute selectors such as `.ui[class*="center aligned"]`.
// Single-word tokens never match those, so also emit 2-3 word runs from every class attribute.
function extractSelectors(content) {
  const out = content.match(/[A-Za-z0-9_-]+/g) || []
  for (const [, value] of content.matchAll(/class\s*=\s*["']([^"']*)["']/g)) {
    const words = value.trim().split(/\s+/)
    for (let n = 2; n <= 3; n++) {
      for (let i = 0; i + n <= words.length; i++) out.push(words.slice(i, i + n).join(' '))
    }
  }
  // The image shortcode renders class="post-image <class arg>", which never appears verbatim in source.
  for (const [, value] of content.matchAll(/\{\{<\s*image\b[^>]*?\bclass\s*=\s*"([^"]*)"/g)) {
    out.push(`post-image ${value.trim()}`)
  }
  return out
}

const SAFELIST = [
    'a', 'abbr', 'blockquote', 'br', 'cite', 'code', 'dd', 'del', 'details', 'dl', 'dt', 'em', 'figcaption',
    'figure', 'hr', 'img', 'input', 'kbd', 'li', 'mark', 'ol', 'p', 'pre', 'section', 'small', 'strong',
    'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul',
    'dimmable', 'dimmed', 'pushable', 'pushed', 'visible', 'animating', 'overlay', 'uncover',
    'active', 'hidden', 'scrolling', 'transition', 'fixed', 'bound', 'top', 'bottom',
    'toc-active', 'copied',
]

/** PurgeCSS options for the given content globs/files. */
function purgeOptions(content) {
  return { content, defaultExtractor: extractSelectors, safelist: SAFELIST, keyframes: true, fontFace: true }
}

module.exports = { extractSelectors, SAFELIST, purgeOptions }
