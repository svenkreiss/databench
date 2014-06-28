.. _quickstart:

Quickstart
==========

Install ``databench`` inside a new ``virtualenv`` (as shown at the top of the :ref:`overview` page) and create the following file structure

.. code-block:: bash

    - workingDir
        - analyses
            - __init__.py
            - helloworld.py
            - templates
                - helloworld.html


First, tell the analyses module that we created a new analysis called ``helloworld`` in the ``__init__.py`` file:

.. code-block:: python

    import analyses.helloworld

Next, create the helloworld backend in ``helloworld.py``:

.. code-block:: python

    """Hello World for Databench."""

    import databench


    helloworld = databench.Analysis('helloworld', __name__)
    helloworld.description = __doc__

    @helloworld.signals.on('connect')
    def onconnect():
        """Run as soon as a browser connects to this."""
        helloworld.signals.emit('status', {'message': 'Hello World'})

And finally, create the frontend in ``helloworld.html``:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head><title>Hello World</title></head>
    <body>
        <p id="output"></p>

        <script src="/static/socket.io/socket.io.min.js"></script>
        <script src="/static/databench.js"></script>
        <script>
            var databench = Databench('helloworld');
            databench.signals.on('status', function(json) {
                document.getElementById('output').innerHTML =
                    json.message;
            });
        </script>
    </body>
    </html>

Now you can run the executable ``databench`` in your ``workingDir`` folder (outside of analyses) which creates a webserver and you can open http://localhost:5000 in your webbrowser. The command line options ``--host`` and ``--port`` set the host and port of the webserver ``--log`` changes the loglevel. For example, calling ``databench --log=DEBUG`` enables all messages; the options are ``NOTSET``, ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` and ``CRITICAL``. You can also create a ``requirements.txt`` file containing other Python packages your analysis needs. An example of this setup is the databench_examples_ repository.

.. _databench_examples: https://github.com/svenkreiss/databench_examples


**Using the** ``base.html`` **Template:** To provide some basic header and footer for an analysis, the ``base.html`` template is available. It is not required to use it, but it includes a range of default libraries that might come in handy. To use it, change the ``helloworld.html`` to

.. code-block:: html

    {% extends "base.html" %}


    {% block title %}Hello World{% endblock %}


    {% block content %}
    <p id="output"></p>
    {% endblock %}


    {% block footerscripts %}
    <script>
        var databench = Databench('helloworld');
        databench.signals.on('status', function(json) {
            document.getElementById('output').innerHTML =
                json.message;
        });
    </script>
    {% endblock %}
