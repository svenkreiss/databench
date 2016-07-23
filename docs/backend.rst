Backend
=======


Analyses Configurations
-----------------------

Example ``analyses/index.yaml``:

.. literalinclude:: ../databench/analyses_packaged/index.yaml
    :language: yaml

Defaults at the global level for ``index.yaml``:

.. code-block:: none

    title: Databench
    description: null
    description_html: null
    author: null
    version: null
    logo_url: /_static/logo.svg
    favicon_url: /_static/favicon.ico
    footer_html: null
    injection_head: ''
    injection_footer: ''
    build: null
    watch: null

    analyses:
      ...

The entries ``injection_head`` and ``injection_footer`` can be overwritten by
placing a ``head.html`` and ``footer.html`` in the analysis folder. This can
be used to insert analytics tracking code.


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


Autoreload
----------

Uses http://www.tornadoweb.org/en/stable/autoreload.html in the backend which
is only activated Databench is run with ``--log INFO`` or ``--log DEBUG``.

To run a single build (i.e. before deploying a production setting for
Databench), use the ``--build`` command line option.


SSL
---

Provide ``--ssl-certfile``, ``--ssl-keyfile`` and ``--ssl-port``.


Analysis
--------

.. autoclass:: databench.Analysis


Meta
----

.. autoclass:: databench.Meta
   :members:


Datastore
---------

.. autoclass:: databench.Datastore
   :members:


AnalysisTestCase
----------------

.. autoclass:: databench.AnalysisTestCase
   :members:
