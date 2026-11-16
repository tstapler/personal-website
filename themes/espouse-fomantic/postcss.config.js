// Used only by this theme's styles partial (css.PostCSS with config="themes/espouse-fomantic"),
// so the shared root postcss.config.js that the espouse theme relies on is untouched.
// Plugins resolve upward to the repo-root node_modules.
const autoprefixer = require('autoprefixer')
const cssnano = require('cssnano')
const purgecss = require('@fullhuman/postcss-purgecss')

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

module.exports = {
  plugins: [
    autoprefixer(),
    purgecss({
      // Class names come from templates, markdown shortcode args, config.toml (icon names),
      // and the shipped JS (Fomantic builds its state classes from string literals).
      content: [
        './layouts/**/*.html',
        './themes/espouse-fomantic/layouts/**/*.html',
        './content/**/*.{md,html}',
        './config.toml',
        './themes/espouse-fomantic/static/js/*.js',
      ],
      defaultExtractor: extractSelectors,
      // State classes toggled at runtime that never appear verbatim in a template.
      safelist: [
        // Elements emitted by rendered Markdown / Hugo (TOC, footnotes, tables); absent from templates.
        'a', 'abbr', 'blockquote', 'br', 'cite', 'code', 'dd', 'del', 'details', 'dl', 'dt', 'em', 'figcaption',
        'figure', 'hr', 'img', 'input', 'kbd', 'li', 'mark', 'ol', 'p', 'pre', 'section', 'small', 'strong',
        'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul',
        'dimmable', 'dimmed', 'pushable', 'pushed', 'visible', 'animating', 'overlay', 'uncover',
        'active', 'hidden', 'scrolling', 'transition', 'fixed', 'bound', 'top', 'bottom',
        'toc-active', 'copied',
      ],
      keyframes: true,
      fontFace: true,
    }),
    cssnano({ preset: ['default', { discardComments: { removeAll: true } }] }),
  ],
}
