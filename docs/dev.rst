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


Now you can run

.. code-block:: bash

	gulp && databench --log DEBUG

and open http://localhost:5000 in a web browser. Now you are ready to submit
pull requests of your contributions. Don't forget to add yourself to
``AUTHORS.rst``.
