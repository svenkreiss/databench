Development
-----------

To contribute to Databench, fork the GitHub repository and clone it to your local machine. Then install your local version in editable mode into the ``virtualenv``:

.. code-block:: bash

	# inside an empty directory:
	git clone https://github.com/<username>/databench.git .

	virtualenv venv
	source venv/bin/activate
	pip install -e .


Now you can run

.. code-block:: bash

	databench

and open http://localhost:5000 in a web browser. Now you are ready to submit pull requests of your contributions.
