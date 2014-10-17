.. _tutorial:

Tutorial
========

This tutorial assumes you have read :ref:`quickstart` and know how to create
an analysis using ``scaffold-databench``.
This tutorial covers custom styling/branding, layouts with Bootstrap 3,
the use of generic UI elements, matplotlib, basic d3.js and
custom API endpoints.

Your input is very welcome. Please don't hesitate to
`file a bug <https://github.com/svenkreiss/databench/issues>`_ or
`send pull requests <https://github.com/svenkreiss/databench/>`_
for typos, mistakes or improvements to this tutorial.


Styling/Branding
----------------

Apply styling by adding

.. code-block:: python

    header_logo = '/analyses_static/logo-header.svg'
    header_title = "My Company's Data Science Experiments"

in ``analyses/__init__.py`` and by adding the logo image file at
``analyses/static/logo-header.svg`` to the file system.


Layouts with Bootstrap 3
------------------------

This is section is not Databench specific. Consult the
`Twitter Bootstrap 3 documentation <http://getbootstrap.com/css/#grid>`_
for a more complete introduction.
For this tutorial, we just focus on creating rows and columns:

.. code-block:: html

    <div class="row">
        <div class="col-md-6">First column</div>
        <div class="col-md-6">Second column</div>
    </div>

which creates one row and two columns. Rows are always 12 units wide.
The two columns above are both six units wide.
The ``md`` is short for medium and controls
at what screen width the two columns are shown as rows: viewing this on
a phone in portrait format for example, the second column will be shown
below the first column. Replacing ``md`` with ``sm`` would show this
content in columns even on small screens. The options are ``xs``, ``sm``,
``md`` and ``lg``.


Generic UI Elements
-------------------

Start from the ``helloworld`` project you created in :ref:`quickstart`.
First, add a button to ``index.html`` by adding

.. code-block:: html

    <button class="btn btn-primary" data-signal-name="run">Run</button>

which creates a *primary* button which is blue. For other colors, replace
``btn-primary`` with a class listed in the
`Bootstrap 3 documentation <http://getbootstrap.com/css/#buttons>`_. The
signal name ``run`` is specified right inside the HTML tag as an attribute. In ``analysis.py``, add a function ``on_run`` to your analysis class

.. code-block:: python

    def on_run(self):
        """Run when button is pressed."""
        self.emit('log', 'Hi. The run button was pressed. Going to sleep.')
        time.sleep(5)
        self.emit('log', 'Waking up again. Run is done.')

and add ``import time`` to the top of ``analysis.py``. That's it. Try it out.
While ``on_run()`` is sleeping for five seconds, the button will look like it is
pressed in (by temporarily adding the CSS class ``active``) and it will
automatically get released (``active`` is removed) when ``on_run()``
finishes.

Next, add a slider. Add to the frontend:

.. code-block:: html

    <label for="sleep_duration">Duration of sleep</label>
    <input type="range" name="sleep_duration" min="1" max="5" step="1" value="3" />

where the signal name is picked up from the ``name`` attribute. The signal has
to be processed by the backend with a function of the form ``on_<signalname>``
again. Add the following to the analysis class in the backend:

.. code-block:: python

    def __init__(self):
        self.sleep_duration = 3

    def on_sleep_duration(self, duration_in_seconds):
        self.sleep_duration = duration_in_seconds

which initializes ``sleep_duration`` to make sure it is always a valid
value and adds the listener function that reponds to changes in the slider
value. Now go back to the ``on_run`` function and replace ``time.sleep(5)``
with ``time.sleep(self.sleep_duration)``. That's it.


Matplotlib
----------

Output from `matplotlib <http://matplotlib.org/>`_ is integrated using
`mpld3 <http://mpld3.github.io/>`_. On the frontend, add

.. code-block:: html

    <div id="mpld3canvas"></div>

and on the backend, add

.. code-block:: python

    fig = plt.figure(figsize=(8, 4))
    # draw something on fig
    self.emit('mpld3canvas', mpld3.fig_to_dict(fig))

for which you will have to have ``matplotlib`` and ``mpld3`` installed
using ``pip install matplotlib mpld3`` have to have it included at the top
of ``analysis.py``:

.. code-block:: python

    import mpld3
    import matplotlib.pyplot as plt

That's it. For a working example, please see the
`mpld3pi demo <https://github.com/svenkreiss/databench_examples/tree/master/analyses/mpld3pi>`_.


If you want to have multiple canvases, add a second ``<div>`` and
append something to the ``id``. The ``id`` only has to start with
``mpld3canvas`` to be automatically connected to the backend.
For example, add ``<div id="mpld3canvas2"></div>`` and add a second
emit ``self.emit('mpld3canvas2', mpld3.fig_to_dict(fig))`` which in this case
would simply show the same ``fig`` on two canvases.


Basic d3.js
-----------

This is a minimal example showing best practices with ``d3.js`` for
Databench. On the frontend, add

.. code-block:: html

    <svg id="canvas" width="300" height="300" />

which is just a SVG canvas in HTML with the id ``canvas``. Go to the
``<script>`` part of the frontend and add the following at the bottom:

.. code-block:: javascript

    // Initialize the VizLogic for our canvas element.
    var my_viz = VizLogic('canvas');

    // Listen for the 'update' signal from the backend. This is the only
    // Databench specific code here.
    databench.on('update', function(json) {
        my_viz(json);
    });

    // Implement the drawing with d3.js.
    function VizLogic(id) {
        // Initialize the d3 selector for the svg element and
        // obtain height and width.
        var svg = d3.select('#'+id),
            height = parseFloat(svg.attr('height')),
            width = parseFloat(svg.attr('width'));

        // Return the function that is used to update the data
        // of what is plotted. The data 'json' has to be of the form:
        // [
        //     {'id': 1, 'x1': 0.1, 'y1': 0.1, 'x2': 0.8, 'y2': 0.1,
        //      'width': 0.05, 'color': 0.1},
        //     {'id': 2, 'x1': 0.1, 'y1': 0.3, 'x2': 0.8, 'y2': 0.3,
        //      'width': 0.05, 'color': 0.2},
        //     {'id': 3, 'x1': 0.1, 'y1': 0.5, 'x2': 0.8, 'y2': 0.5,
        //      'width': 0.05, 'color': 0.3},
        //     ...
        // ]
        return function(json) {
            // The new 'json' data (has to be an array) is compared to the
            // existing elements with the class 'line'. By default, d3.js
            // uses the element index in the array as the key to associate
            // elements from previous data calls with the new ones. This
            // breaks when data is inserted in the middle of arrays.
            // Therefore, a function that returns the 'key' can be specified
            // as the second argument to data(). Here, the key is the element
            // with the name 'id'.
            lines = svg.selectAll(".line").data(json, function(d) { return d.id; });

            // Specify what happens how to initialize a new element. Note
            // that lines.transition() is also applied to elements that just
            // entered. Specify the initial attributes here (like width 0.0)
            // and then set the actual attributes it should animate to in
            // transition() below.
            //
            // Every attribute is given either a value (like for stroke-width)
            // or the value is obtained by calling a function with the data
            // element, in this example it could be
            //    {'id': 1, 'x1': 0.1, 'y1': 0.1, 'x2': 0.8, 'y2': 0.1,
            //     'width': 0.05, 'color': 0.1}
            // and the function calculates the value. Below, the functions
            // scale x1, y1, x2 and y2 from a range of [0,1] to [0,width]
            // and [0,height] in pixels and convert a color in the range
            // [0,1] to a color of the form #123456 by using the d3.hsl()
            // function.
            lines.enter()
                .append("svg:line")
                .attr("class", "line")
                .attr("x1", function(d) { return width*d.x1; })
                .attr("y1", function(d) { return height*d.y1; })
                .attr("x2", function(d) { return width*d.x2; })
                .attr("y2", function(d) { return height*d.y2; })
                .style("stroke", function(d) {
                    return d3.hsl(100,d.color,d.color).toString();
                })
                .style("stroke-width", 0.0);

            // Specify what to do for changing attributes. Here, only the
            // stroke-width is updated and all other attributes are
            // assumed to stay constant after the element entered.
            // The duration the animation takes to update the value is given
            // with duration() in milliseconds.
            lines.transition()
                .duration(250)
                .style("stroke-width", function(d) { return width*d.width; });

            // Specify what to do when an element is missing in the new
            // data. Here, just remove it.
            lines.exit()
                .remove();

        };
    }

On the backend, create some data and send it to the frontend with the
``update`` signal:

.. code-block:: python

    data = [
        {'id': 1, 'x1': 0.1, 'y1': 0.1, 'x2': 0.8, 'y2': 0.5,
         'width': 0.05, 'color': 0.5},
        {'id': 2, 'x1': 0.1, 'y1': 0.3, 'x2': 0.8, 'y2': 0.7,
         'width': 0.05, 'color': 0.7},
        {'id': 3, 'x1': 0.1, 'y1': 0.5, 'x2': 0.8, 'y2': 0.9,
         'width': 0.05, 'color': 0.9},
    ]
    self.emit('update', data)
    # update with some new data after a short wait
    time.sleep(1)
    data2 = [
        {'id': 1, 'x1': 0.1, 'y1': 0.1, 'x2': 0.8, 'y2': 0.5,
         'width': 0.2, 'color': 0.5},
        {'id': 2, 'x1': 0.1, 'y1': 0.3, 'x2': 0.8, 'y2': 0.7,
         'width': 0.2, 'color': 0.7},
        {'id': 3, 'x1': 0.1, 'y1': 0.5, 'x2': 0.8, 'y2': 0.9,
         'width': 0.2, 'color': 0.9},
    ]
    self.emit('update', data2)

That's it.


Custom API Endpoints
--------------------

Coming soon ...


A working example of the analysis that you get from following all parts of this
tutorial is available in the
`Databench examples repository <https://github.com/svenkreiss/databench_examples>`_
under the name
`tutorial <https://github.com/svenkreiss/databench_examples/tree/master/analyses/tutorial>`_.
