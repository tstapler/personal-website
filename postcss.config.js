const purgecss = require('@fullhuman/postcss-purgecss')

module.exports = {
  plugins: [
        purgecss({
            content: [
                './themes/espouse/layouts/**/*.html',
                './themes/espouse/static/js/*.js',
                './themes/espouse-fomantic/layouts/**/*.html',
                './themes/espouse-fomantic/static/js/*.js',
                './layouts/**/*.html',
                './content/**/*.{md,html}',
                './static/js/*.js',
                './node_modules/semantic-ui-css/**/*.js',
                // Built by the image shortcode at render time, so no file contains the full attribute value
                { raw: 'post-image left floated post-image right floated', extension: 'html' }
              ],
          safelist: {
                // Tags that only appear in rendered markdown, never in a template
                standard: ["hr", "blockquote", "pre", "code", "table", "thead", "tbody", "th", "td", "tr", "ul", "ol", "li", "a", "p", "em", "strong", "img", "figure", "figcaption", "h1", "h2", "h3", "h4", "h5", "h6", "book", "ui", "left", "vertical", "menu", "inverted", "sidebar", "labeled", "icon", "item", "active", "header", "pushable", "pushed", "visible", "overlay"],
                greedy:[/post-image/, /floated/, /centered/, /container/, /text/, /aligned/, /center/, /content/, /ui/, /sidebar/, /menu/, /icon/]

          }

        }),
      require('postcss-url')({url: 'inline'}),
      require('cssnano')({
            preset: 'default',
        }),
      require('postcss-clean')({})
  ]
};
