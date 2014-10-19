.. _tutorial:

Tutorial
========

This tutorial assumes you have read :ref:`quickstart` and know how to create
an analysis using ``scaffold-databench``.
This tutorial covers custom styling/branding, layouts with Bootstrap 3,
the use of generic UI elements, matplotlib and basic d3.js.

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

    <svg id="canvas_basic" width="300" height="300" />

which is just a SVG canvas in HTML with the id ``canvas``. Go to the
``<script>`` part of the frontend and add the following at the bottom:

.. code-block:: javascript

    // Initialize the VizBasic for our canvas element.
    var viz_basic = VizBasic('canvas_basic');

    // Listen for the 'update' signal from the backend. This is the only
    // Databench specific code here.
    databench.on('update_basic', function(json) {
        viz_basic(json);
    });

    // Implement the drawing with d3.js.
    function VizBasic(id) {
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
``update_basic`` signal:

.. code-block:: python

    data = [
        {'id': 1, 'x1': 0.1, 'y1': 0.1, 'x2': 0.8, 'y2': 0.5,
         'width': 0.05, 'color': 0.5},
        {'id': 2, 'x1': 0.1, 'y1': 0.3, 'x2': 0.8, 'y2': 0.7,
         'width': 0.05, 'color': 0.7},
        {'id': 3, 'x1': 0.1, 'y1': 0.5, 'x2': 0.8, 'y2': 0.9,
         'width': 0.05, 'color': 0.9},
    ]
    self.emit('update_basic', data)
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
    self.emit('update_basic', data2)

That's it.


A Plot with d3.js
-----------------

On the frontend add some styling for the axes to the page.

.. code-block:: html

    {% block head %}
    <style>
    .axis path, .axis line {
      fill: none;
      stroke: #000;
      shape-rendering: crispEdges;
    }
    </style>
    {% endblock %}

Then insert another canvas element:

.. code-block:: html

    <svg id="canvas_plot" width="300" height="300" />

and again add this to the bottom of the ``<script>`` tag:

.. code-block:: javascript

    // Initialize the VizPlot for our canvas element.
    var viz_plot = VizPlot('canvas_plot');

    // Listen for the 'update' signal from the backend. This is the only
    // Databench specific code here.
    databench.on('update_plot', function(json) {
        viz_plot(json);
    });

    // Implement a basic plot with d3.js.
    //
    // This demos some fundamental principles of d3.js without using d3 layouts.
    // Layouts are extremely powerful, but confuse a first exposure to
    // d3.js. Here, no layout is used, but scales and axes are introduced. For
    // a full example with d3 layouts, please see the Histogram example from
    // Mike Bostock: http://bl.ocks.org/mbostock/3048450
    function VizPlot(id) {
        // Initialize the d3 selector for the svg element and
        // obtain height and width.
        var svg = d3.select('#'+id),
            height = parseFloat(svg.attr('height')),
            width = parseFloat(svg.attr('width'));

        // Specify margins of the plot within the svg element in pixels.
        var margin = {'left': 40, 'right': 20, 'top': 20, 'bottom': 20}

        // Setup scales. 'domain()' specifies the range of the variables is in
        // the data and 'range()' specifies the range of the coordinate on the
        // screen in pixels. The funcitons 'x' and 'y' are a variable
        // transformation from input data to pixels.
        //
        // Note that the range for x is 20 to 280 pixels. The range for y is
        // 280 to 20 pixels with the larger number first. This is because the
        // number of pixels are counted from the top of the SVG, but we want our
        // y axis to start at the bottom.
        var x = d3.scale.linear()
                    .domain([0, 5])
                    .range([margin.left, width-margin.right]);
        var y = d3.scale.linear()
                    .domain([0, 1.5])
                    .range([height-margin.bottom, margin.top]);
        // Now we are just going to test the variable transformations. The
        // output will appear in the browser JavaScript console, but also in
        // the log window in this analysis.
        console.log('Testing the transformations x() and y(). Output in pixels:');
        console.log(x(0));
        console.log(x(2));
        console.log(x(4));
        console.log(y(0));
        console.log(y(0.5));
        console.log(y(1.0));

        // Elements inside of SVG are drawn in the order they are added. Below
        // we are going to add the axes, but we want the axes to stay in front
        // of the content of the plot. So technically, we need to add the
        // content of the plot (the bars of the histogram) now and only then we
        // can add the axes. We cannot add the content now, but we can add a
        // group 'g' here for the content and later we will not draw the bars
        // into 'svg' but into 'g'.
        var plot_content = svg.append('g');

        // The x-axis, is effectively a visual representation of the
        // transformation defined with x(). So d3 has an 'axis()' function
        // packaged that takes a scale and turns it into a drawable element:
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");
        // Draw the x-axis. The y-position for drawing an x-axis is always 0.
        // So one has to apply a group element 'g' first whose coordinates are
        // shifted such that y=0 is where we want to draw the x-axis. We can
        // either use 'height-margin.bottom' as the position in pixels, or
        // we can use the transformation y(0) to get the same result, but in a
        // cleaner way.
        svg.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,'+y(0)+')')
            .call(xAxis);
        // And the same for the y-axis:
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");
        svg.append('g')
            .attr('class', 'y axis')
            .attr('transform', 'translate('+x(0)+',0)')
            .call(yAxis);

        // Return the function that is used to update the data
        // of what is plotted. The data 'json' has to be an array/list numbers.
        // For example: [0.4, 0.5, 0.3, 0.2, 0.1]
        //
        // Please see the 'basic d3.js' example above for comments on the data
        // flow. Here, only the new parts are commented.
        return function(json) {
            lines = plot_content.selectAll(".line").data(json);

            // The x-coordinates are derived from the index of the data element.
            // So for any attribute where the value is dynamically calculated
            // with a function, the arguments d and i of the function are the
            // element d of the data array and the index i. For the histogram,
            // drawing the box for x=[0,1) is done with a line centered at 0.5.
            // So in general, we take the index plus 0.5 and transform it into
            // pixels: x(i+0.5).
            //
            // The width of that line in pixels is calculated by the position
            // in pixels of at x=1 minus x=0: x(1)-x(0).
            lines.enter()
                .append("svg:line")
                .attr("class", "line")
                .attr("x1", function(d, i) { return x(i+0.5); })
                .attr("y1", y(0.0))
                .attr("x2", function(d, i) { return x(i+0.5); })
                .attr("y2", function(d) { return y(d); })
                .style("stroke", "#55aa55")
                .style("stroke-width", function(d) { return x(1)-x(0); });

            lines.transition()
                .duration(250)
                .attr("y2", function(d) { return y(d); });

            lines.exit()
                .remove();

        };
    }

On the backend, create an array with five random numbers and send it to the
frontend. Then wait one second and send a different array with five random
numbers to the frontend to demo the dynamically changing plot:

.. code-block:: python

    self.emit('update_plot', [random.random() for i in xrange(5)])
    time.sleep(1)
    self.emit('update_plot', [random.random() for i in xrange(5)])

That's it.


Wrapping Up
-----------

A working example of the analysis that you get from following all parts of this
tutorial is available in the
`Databench examples repository <https://github.com/svenkreiss/databench_examples>`_
under the name
`tutorial <https://github.com/svenkreiss/databench_examples/tree/master/analyses/tutorial>`_.

As mentioned before, please feel free to send comments about this tutorial.
