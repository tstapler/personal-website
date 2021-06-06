const purgecss = require('@fullhuman/postcss-purgecss')

module.exports = {
  plugins: [
       // purgecss({
       //     content: [
       //         './themes/espouse/layouts/**/*.html',
       //         './themes/espouse/assets/js/*.js',
       //         './themes/espouse/static/js/*.js',
       //         './layouts/**/*.html',
       //         './static/js/*.js'
       //       ],
       //   safelist: {
       //         standard: ["book"],
       //         greedy:[/container/, /text/, /aligned/, /center/, /content/]
       //
       //   }
       //
       // }),
      require('postcss-url')({url: 'inline'}),
      require('cssnano')({
            preset: 'default',
        }),
      require('postcss-clean')({})
  ]
};
