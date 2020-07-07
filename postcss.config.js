module.exports = {
  plugins: {
      '@fullhuman/postcss-purgecss': {
          content: [
              './themes/espouse/layouts/**/*.html', 
              './themes/espouse/assets/js/*.js',
              './themes/espouse/static/js/*.js',
              './layouts/**/*.html',
              './static/js/*.js'
            ],
          whitelist: [
              'highlight',
              'language-bash',
              'pre',
              'video',
              'code',
              'content',
              'h3',
              'h4',
              'ul',
              'li'
          ]
      },
      autoprefixer: {},
      cssnano: {preset: 'default'}
  }
};
