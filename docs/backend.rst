Backend
=======


Readme configurations
---------------------

title, description, watch, build


Example ``analyses/README.md``:

.. code-block:: markdown

    <!--
    title: Databench Examples
    description: Describe all the analyses.
    build: cd analyses; gulp
    watch: analyses/js/**/*.jsx
    -->

    Some helpful text.


Example ``analyses/gulpfile.js`` for React and ES6:

.. code-block:: javascript

    var gulp = require('gulp');
    var browserify = require('browserify');
    var babelify = require('babelify');
    var source = require('vinyl-source-stream');
    var buffer = require('vinyl-buffer');
    var sourcemaps = require('gulp-sourcemaps');
    // var uglify = require('gulp-uglify');


    gulp.task('build', function () {
        browserify({entries: 'js/index.jsx', extensions: ['.jsx'], debug: true})
            .transform('babelify', {presets: ['es2015', 'stage-1', 'react']})
            .bundle()
            .pipe(source('bundle.js'))
            .pipe(buffer())
            .pipe(sourcemaps.init({ loadMaps: true }))
            // .pipe(uglify())
            .pipe(sourcemaps.write('./'))
            .pipe(gulp.dest('static'));
    });


    gulp.task('default', ['build']);


Analysis
--------

.. autoclass:: databench.Analysis


Meta
----

.. autoclass:: databench.Meta
   :members: render_index
