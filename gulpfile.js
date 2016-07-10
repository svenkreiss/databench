var gulp = require('gulp');
var babel = require('gulp-babel');
var babelify = require('babelify');
var browserify = require('browserify');
var buffer = require('vinyl-buffer');
var source = require('vinyl-source-stream');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');


gulp.task('browser', function() {
  var bundler = browserify({ entries: 'js/src/main.js', debug: true });
  bundler.transform('babelify', { presets: ['es2015', 'stage-1'] });

  bundler.bundle()
    .pipe(source('databench.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({ loadMaps: true }))
    // .pipe(uglify())
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest('js/build/browser/'))
    .pipe(gulp.dest('databench/static/'));
});


gulp.task('node_client', function() {
  return gulp.src('js/src/*.js')
    .pipe(sourcemaps.init())
    .pipe(babel({presets: ['es2015', 'stage-1']}))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest('js/build/node_client/'));
});


gulp.task('default', ['browser', 'node_client']);
