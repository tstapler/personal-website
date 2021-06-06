const gulp = require('gulp');
const log = require('fancy-log');
const critical = require('critical').stream;
const gzip = require('gulp-gzip')
const debug = require('gulp-debug')

// Generate & Inline Critical-path CSS
gulp.task('critical', () => {
  return gulp
    .src('public/**/*.html')
    .pipe(
      critical({
        base: 'public/',
        inline: true,
      })
    )
    .on('error', err => {
      log.error(err.message);
    })
    .pipe(gulp.dest('public'));
});

gulp.task('compress', () =>{
  return gulp.src(['public/**/*.html', "public/**/*.css", "public/**/*.js"])
    .pipe(gzip())
    .pipe(gulp.dest("public"));
});
