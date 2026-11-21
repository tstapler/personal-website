// Used only by this theme's styles partial (css.PostCSS with config="themes/espouse-fomantic") and webpack's
// postcss-loader. The Bazel build purges the finished site instead: see optimize_site.mjs.
const autoprefixer = require('autoprefixer')
const cssnano = require('cssnano')
const purgecss = require('@fullhuman/postcss-purgecss')
const { purgeOptions } = require('./postcss.shared')

module.exports = {
  plugins: [
    autoprefixer(),
    // Class names come from templates, markdown shortcode args, config.toml (icon names),
    // and the shipped JS (Fomantic builds its state classes from string literals).
    purgecss(purgeOptions([
      './layouts/**/*.html',
      './themes/espouse-fomantic/layouts/**/*.html',
      './content/**/*.{md,html}',
      './config.toml',
      './themes/espouse-fomantic/static/js/*.js',
    ])),
    cssnano({ preset: ['default', { discardComments: { removeAll: true } }] }),
  ],
}
