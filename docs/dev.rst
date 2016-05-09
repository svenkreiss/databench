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
	pip install -e .[tests]

    # js dependencies
    npm install -g gulp
    npm install

    # install pre-commit hook to check linting
    flake8 --install-hook


Now you can:

.. code-block:: bash

    # run Databench
	gulp && databench --log DEBUG
    # and open http://localhost:5000 in a web browser

    # run tests
    nosetests -vv --with-coverage --cover-package=databench --cover-erase --cover-inclusive

For new contributions, create a feature branch and submit a Pull Request.
Don't forget to add yourself to ``AUTHORS.rst``.
