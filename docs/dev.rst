Development
-----------

To contribute to Databench, fork the GitHub repository and clone it to your
local machine. Then install your local version in editable mode into a
``virtualenv``:

.. code-block:: bash

	# inside an empty directory:
	git clone https://github.com/<username>/databench.git .

	virtualenv venv
	source venv/bin/activate
	pip install -e .


Now you can run

.. code-block:: bash

	databench --log DEBUG

and open http://localhost:5000 in a web browser. Now you are ready to submit
pull requests of your contributions. Don't forget to add yourself to
``AUTHORS.rst``.

To develop on the JavaScript library, install `gulp` with `npm install -g gulp`
and the package with `npm install` which will pull in a few dependencies.
Rebuild the `js` library and launch in one command with
`gulp && databench --log DEBUG`.
