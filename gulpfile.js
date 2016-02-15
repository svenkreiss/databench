var gulp = require('gulp');
var babelify = require('babelify');
var browserify = require('browserify');
var buffer = require('vinyl-buffer');
var source = require('vinyl-source-stream');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');

gulp.task('default', function () {
    var bundler = browserify({
        entries: 'js/main.js',
        debug: true
    });
    bundler.transform('babelify', {presets: ['es2015', 'stage-1']});

    bundler.bundle()
        // .on('error', function (err) { console.error(err); })
        .pipe(source('databench_04.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({ loadMaps: true }))
        // .pipe(uglify()) // Use any gulp plugins you want now
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('databench/static'));
});
