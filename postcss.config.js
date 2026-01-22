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
                './static/js/*.js',
                './node_modules/semantic-ui-css/**/*.js'
              ],
          safelist: {
                standard: ["book", "ui", "left", "vertical", "menu", "inverted", "sidebar", "labeled", "icon", "item", "active", "header", "pushable", "pushed", "visible", "overlay"],
                greedy:[/container/, /text/, /aligned/, /center/, /content/, /ui/, /sidebar/, /menu/, /icon/]

          }

        }),
      require('postcss-url')({url: 'inline'}),
      require('cssnano')({
            preset: 'default',
        }),
      require('postcss-clean')({})
  ]
};
