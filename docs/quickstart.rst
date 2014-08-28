.. _quickstart:

Quickstart
==========

Install ``databench`` (as shown at the top of the :ref:`overview` page) and create the following file structure

.. code-block:: bash

    - workingDir/
        - analyses/
            - __init__.py
            - helloworld/
                - __init__.py
                - analysis.py
                - index.html
                - thumbnail.png (optional)


First, tell the analyses module that we created a new analysis called ``helloworld``. Add the following to the ``analyses/__init__.py`` file:

.. code-block:: python

    """A test setup showing 'Hello World' in Databench."""

    import helloworld.analysis

Next, create the helloworld backend in ``analysis.py``:

.. code-block:: python

    """Hello World for Databench."""

    import databench


    class Analysis(databench.Analysis):

        def on_connect(self):
            """Run as soon as a browser connects to this."""
            self.emit('status', {'message': 'Hello World'})


    META = databench.Meta('helloworld', __name__, __doc__, Analysis)

And finally, create the frontend in ``index.html``:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head><title>Hello World</title></head>
    <body>
        <p id="output"></p>

        <script src="/static/jquery/jquery-2.1.1.min.js"></script>
        <script src="/static/databench.js"></script>
        <script>
            var databench = Databench();
            databench.on('status', function(json) {
                document.getElementById('output').innerHTML =
                    json.message;
            });
        </script>
    </body>
    </html>

Now you can run the executable ``databench`` in your ``workingDir`` folder (outside of analyses) which creates a webserver and you can open http://localhost:5000 in your webbrowser. The command line options ``--host`` and ``--port`` set the host and port of the webserver ``--log`` changes the loglevel. For example, calling ``databench --log=DEBUG`` enables all messages; the options are ``NOTSET``, ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` and ``CRITICAL``. You can also create a ``requirements.txt`` file containing other Python packages your analysis needs. An example of this setup is the databench_examples_ repository.

.. _databench_examples: https://github.com/svenkreiss/databench_examples


**Using the** ``base.html`` **Template:** To provide some basic header and footer for an analysis, the ``base.html`` template is available. It is not required to use it, but it includes a range of default libraries that might come in handy. To use it, change the ``index.html`` to

.. code-block:: html

    {% extends "base.html" %}


    {% block title %}Hello World{% endblock %}


    {% block content %}
    <p id="output"></p>
    {% endblock %}


    {% block footerscripts %}
    <script>
        var databench = Databench();
        databench.on('status', function(json) {
            document.getElementById('output').innerHTML =
                json.message;
        });
    </script>
    {% endblock %}
