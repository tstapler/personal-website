// Gulp and node
var gulp = require('gulp');
var u = require('gulp-util');
var log = u.log;
var c = u.colors;
var del = require('del');
var spawn = require('child_process').spawn;
var sequence = require('run-sequence');
var tasks = require('gulp-task-listing');

// Basic workflow plugins
var prefix = require('gulp-autoprefixer');
var bs = require('browser-sync');
var reload = bs.reload;

// Performance workflow plugins
var concat = require('gulp-concat');
var mincss = require('gulp-minify-css');
var imagemin = require('gulp-imagemin');
var uglify = require('gulp-uglify');
var critical = require('critical').stream;
var postcss = require('gulp-postcss');
var uncss = require('postcss-uncss');

// Performance testing plugins
var psi = require('psi');

var dist_folder = 'deployment/dist/' + process.env.SITE_NAME + '/'
var pre_dist_folder = 'deployment/pre_dist/' + process.env.SITE_NAME + '/'

// -----------------------------------------------------------------------------
// UnCSS Task
//
// Checks the site's usage of Bootstrap and strips unused styles out. Outputs
// the resulting files in the css/ directory where they will be combined and
// minified by a separate task.
//
// Note: this task requires a local server to be running because it references
// the actual compiled site to calculate the unused styles.
// -----------------------------------------------------------------------------
gulp.task('uncss', function() {
  var plugins = [
    uncss({
          html: [
            pre_dist_folder + '**/*.html' 
          ]
        })
  ];
  return gulp.src([
    pre_dist_folder + 'css/*.css',
    ])
    .pipe(postcss(plugins))
    .pipe(gulp.dest(dist_folder + '/css/'));
});


// -----------------------------------------------------------------------------
// Generate critical-path CSS
//
// All styles should be directly applying to an element visible when your
// website renders. If the user has to scroll even a small amount, it's not
// critical CSS.
// -----------------------------------------------------------------------------
gulp.task('critical', function (cb) {
  return gulp.src(dist_folder + '**/*.html')
    .pipe(critical({
      base: dist_folder, 
      inline: true, 
      minify: true,
      css: [
        dist_folder + 'css/all.css', 
        dist_folder + 'css/photoGallery.css']
    }))
    .on('error', function(err) { u.log(u.colors.red(err.message)); })
    .pipe(gulp.dest(dist_folder));
});

// -----------------------------------------------------------------------------
// Minify SVGs and compress images
//
// It's good to maintain high-quality, uncompressed assets in your codebase.
// However, it's not always appropriate to serve such high-bandwidth assets to
// users, in order to reduce mobile data plan usage.
// -----------------------------------------------------------------------------
gulp.task('imagemin', function() {
  return gulp.src('_img/**/*')
    .pipe(imagemin({
      progressive: true,
      svgoPlugins: [{removeViewBox: false}]
    }))
    .pipe(gulp.dest('img'));
});

// -----------------------------------------------------------------------------
// Hugo
//
// Regenerate the Hugo site when files are touched. The --watch flag is not
// used because the bs/watch tasks will handle the "watching" of the files.
// -----------------------------------------------------------------------------
gulp.task('hugo', function() {
  bs.notify('<span style="color: grey">Running:</span> Hugo task');

  return spawn('hugo', [], {stdio: 'inherit'})
    .on('close', reload);
});

// -----------------------------------------------------------------------------
// Hugo Serve
//
// This command is used exclusively by Travis to start Hugo in the background
// then run tests against it.
// -----------------------------------------------------------------------------
gulp.task('hugo-serve', function(callback) {
  spawn('hugo', ['serve'], {stdio: 'inherit'})
    .on('close', callback)
});

// -----------------------------------------------------------------------------
// Browser Sync
//
// Makes web development better by eliminating the need to refresh. Essential
// for CSS development and multi-device testing.
// -----------------------------------------------------------------------------
gulp.task('browser-sync', function() {
  bs({
    server: './_site/'
  });
});

// -----------------------------------------------------------------------------
// Watch tasks
//
// These tasks are run whenever a file is saved. Don't confuse the files being
// watched (gulp.watch blobs in this task) with the files actually operated on
// by the gulp.src blobs in each individual task.
//
// A few of the performance-related tasks are excluded because they can take a
// bit of time to run and don't need to happen on every file change. If you want
// to run those tasks more frequently, set up a new watch task here.
// -----------------------------------------------------------------------------
gulp.task('watch', function() {
  gulp.watch('_sass/**/*.scss', ['css']);
  gulp.watch('_img/**/*', ['imagemin']);
  gulp.watch(['./**/*.{md,html}', '!./_site/**/*.*', '!./node_modules/**/*.*'], ['hugo']);
});

// -----------------------------------------------------------------------------
// Convenience task for development.
//
// This is the command you run to warm the site up for development. It will do
// a full build, open BrowserSync, and start listening for changes.
// -----------------------------------------------------------------------------
gulp.task('bs', ['css', 'js', 'imagemin', 'hugo', 'watch']);

// -----------------------------------------------------------------------------
// Performance test: Phantomas
//
// Phantomas can be used to test granular performance metrics. This example
// ensures that the site never exceeds a specific number of HTTP requests.
// -----------------------------------------------------------------------------
gulp.task('phantomas', function() {
  var limit = 5;
  var phantomas = spawn('./node_modules/.bin/phantomas', ['--url', 'http://localhost:1313', '--assert-requests=' + limit]);

  // Uncomment this block to see the full Phantomas output.
  // phantomas.stdout.on('data', function (data) {
  //   data = data.toString().slice(0, -1);
  //   log('Phantomas:', data);
  // });

  // Catch any errors.
  phantomas.on('error', function (err) {
    log(err);
  });

  // Log results to console.
  phantomas.on('close', function (code) {
    // Exit status of 0 means success!
    if (code === 0) {
      log('Phantomas:', c.green('✔︎ Yay! The site makes ' + limit + ' or fewer HTTP requests.'));
    }

    // Exit status of 1 means the site failed the test.
    else if (code === 1) {
      log('Phantomas:', c.red('✘ Rats! The site makes more than ' + limit + ' HTTP requests.'));
      process.exit(code);
    }

    // Other exit codes indicate problems with the test itself, not a failed test.
    else {
      log('Phantomas:', c.bgRed('', c.black('Something went wrong. Exit code'), code, ''));
      process.exit(code);
    }
  });
});

// -----------------------------------------------------------------------------
// Performance test: Critical CSS
//
// This test checks our generated critical CSS to make sure there are no external
// requests which would block rendering. Having external calls defeats the entire
// purpose of inlining the CSS, since the external call blocks rendering.
// -----------------------------------------------------------------------------
gulp.task('critical-test', function () {
  // Spawn our critical CSS test and suppress all output.
  var critical = spawn('./examples/critical/critical.sh', ['>/dev/null']);

  // Catch any errors.
  critical.on('error', function (err) {
    log(err);
  });

  // Log results to console.
  critical.on('close', function (code) {
    // Exit status of 0 means success!
    if (code === 0) {
      log('Critical:', c.green('✔︎ Yay! The generated CSS makes zero external requests.'));
    }

    // Exit status of anything else means the test failed.
    else {
      log('Critical:', c.red('✘ Rats! The generated CSS makes ' + code + ' external requests.'));
      process.exit(code);
    }
  });
});

// -----------------------------------------------------------------------------
// Performance test: run everything at once
//
// Having a task that simply runs other tasks is nice for Travis or other CI
// solutions, because you only have to specify one command, and gulp handles
// the rest.
// -----------------------------------------------------------------------------
gulp.task('test', function (callback) {
  sequence(
    'hugo-serve',
    'critical-test',
    'phantomas',
    'psi',
    callback
  );
});

// -----------------------------------------------------------------------------
// Default: load task listing
//
// Instead of launching some unspecified build process when someone innocently
// types `gulp` into the command line, we provide a task listing so they know
// what options they have without digging into the file.
// -----------------------------------------------------------------------------
gulp.task('help', tasks);
gulp.task('default', ['help']);
